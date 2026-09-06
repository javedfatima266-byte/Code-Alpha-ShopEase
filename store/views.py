from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST

from .models import Category, Product, Cart, CartItem, Order, OrderItem, UserProfile
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, CheckoutForm


def _merge_session_cart(request, old_session_key):
    """Safely migrate any items from guest session cart to the logged-in user cart."""
    if not old_session_key or not request.user.is_authenticated:
        return
    old_cart = Cart.objects.filter(session_key=old_session_key).first()
    if old_cart:
        user_cart, _ = Cart.objects.get_or_create(user=request.user)
        for s_item in old_cart.items.all():
            u_item, created_item = CartItem.objects.get_or_create(
                cart=user_cart,
                product=s_item.product,
                defaults={'quantity': s_item.quantity}
            )
            if not created_item:
                u_item.quantity = min(
                    u_item.quantity + s_item.quantity,
                    s_item.product.stock_quantity
                )
                u_item.save()
        old_cart.delete()


def _get_or_create_cart(request):
    """Retrieve existing cart or create a new one based on authentication or session."""
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        return cart
    else:
        cart, created = Cart.objects.get_or_create(session_key=session_key)
        return cart


def home_view(request):
    featured_products = Product.objects.filter(
        available=True,
        is_featured=True
    ).select_related('category')[:8]

    if not featured_products.exists():
        featured_products = Product.objects.filter(
            available=True
        ).select_related('category')[:8]

    categories = Category.objects.all()
    new_arrivals = Product.objects.filter(
        available=True
    ).select_related('category').order_by('-created_at')[:4]

    context = {
        'featured_products': featured_products,
        'categories': categories,
        'new_arrivals': new_arrivals,
    }
    return render(request, 'home.html', context)


def product_list_view(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True).select_related('category')

    # Category filter from URL slug or GET parameter
    cat_param = category_slug or request.GET.get('category')
    if cat_param:
        category = get_object_or_404(Category, slug=cat_param)
        products = products.filter(category=category)

    # Search keyword filter
    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )

    # Price range filter
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    if min_price:
        try:
            products = products.filter(price__gte=Decimal(min_price))
        except Exception:
            pass
    if max_price:
        try:
            products = products.filter(price__lte=Decimal(max_price))
        except Exception:
            pass

    # Availability filter
    availability = request.GET.get('availability', 'all')
    if availability == 'in_stock':
        products = products.filter(stock_quantity__gt=0)

    # Sorting
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    else:  # newest
        products = products.order_by('-created_at')

    # Pagination: 8 products per page
    paginator = Paginator(products, 8)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.get_page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.get_page(1)

    context = {
        'category': category,
        'categories': categories,
        'products': page_obj,
        'query': query,
        'min_price': min_price,
        'max_price': max_price,
        'availability': availability,
        'sort_by': sort_by,
        'total_count': products.count(),
    }
    return render(request, 'products.html', context)


def product_detail_view(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    related_products = Product.objects.filter(
        category=product.category,
        available=True
    ).exclude(id=product.id)[:4]

    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'product_detail.html', context)


def cart_view(request):
    cart = _get_or_create_cart(request)
    cart_items = cart.items.select_related('product').all()
    subtotal = cart.get_subtotal()
    shipping_cost = cart.get_shipping_cost()
    free_shipping_remaining = max(Decimal('0.00'), Decimal('75.00') - subtotal)

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'items': cart_items,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'free_shipping_remaining': free_shipping_remaining,
        'total': cart.get_total(),
    }
    return render(request, 'cart.html', context)


def add_to_cart_view(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)
    cart = _get_or_create_cart(request)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1

    if quantity < 1:
        quantity = 1

    if product.stock_quantity < 1:
        messages.error(request, f"Sorry, '{product.name}' is currently out of stock.")
        return redirect(request.META.get('HTTP_REFERER', 'cart'))

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 0}
    )

    new_quantity = cart_item.quantity + quantity
    if new_quantity > product.stock_quantity:
        cart_item.quantity = product.stock_quantity
        cart_item.save()
        messages.warning(
            request,
            f"Maximum available stock for '{product.name}' is {product.stock_quantity}. Cart updated to maximum available."
        )
    else:
        cart_item.quantity = new_quantity
        cart_item.save()
        messages.success(request, f"Added {quantity} x '{product.name}' to your cart.")

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'cart_count': cart.get_total_items(),
            'message': f"Added '{product.name}' to cart."
        })

    return redirect(request.META.get('HTTP_REFERER', 'cart'))


@require_POST
def update_cart_view(request, item_id):
    cart = _get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    action = request.POST.get('action')
    quantity_param = request.POST.get('quantity')

    if action == 'increase':
        if cart_item.quantity < cart_item.product.stock_quantity:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f"Updated quantity for '{cart_item.product.name}'.")
        else:
            messages.warning(
                request,
                f"Cannot add more. Only {cart_item.product.stock_quantity} units available in stock."
            )
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            messages.success(request, f"Updated quantity for '{cart_item.product.name}'.")
        else:
            cart_item.delete()
            messages.info(request, f"Removed '{cart_item.product.name}' from your cart.")
    elif quantity_param:
        try:
            qty = int(quantity_param)
            if qty <= 0:
                cart_item.delete()
                messages.info(request, f"Removed '{cart_item.product.name}' from your cart.")
            elif qty > cart_item.product.stock_quantity:
                cart_item.quantity = cart_item.product.stock_quantity
                cart_item.save()
                messages.warning(
                    request,
                    f"Capped to available stock of {cart_item.product.stock_quantity} units."
                )
            else:
                cart_item.quantity = qty
                cart_item.save()
                messages.success(request, f"Quantity updated for '{cart_item.product.name}'.")
        except ValueError:
            pass

    return redirect('cart')


def remove_from_cart_view(request, item_id):
    cart = _get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    name = cart_item.product.name
    cart_item.delete()
    messages.info(request, f"Removed '{name}' from your cart.")
    return redirect('cart')


def clear_cart_view(request):
    cart = _get_or_create_cart(request)
    cart.items.all().delete()
    messages.info(request, "Your shopping cart has been cleared.")
    return redirect('cart')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            full_name = form.cleaned_data['full_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Split name into first and last
            parts = full_name.strip().split(' ', 1)
            first_name = parts[0]
            last_name = parts[1] if len(parts) > 1 else ''

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            UserProfile.objects.create(user=user)

            # Automatically log in the registered user
            old_session_key = request.session.session_key
            login(request, user)
            _merge_session_cart(request, old_session_key)

            messages.success(request, f"Welcome to ShopEase, {full_name}! Your account was created successfully.")
            return redirect('home')
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    next_url = request.GET.get('next') or request.POST.get('next') or 'home'

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username'].strip()
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me')

            # Support login via username OR email
            user = authenticate(request, username=username_or_email, password=password)
            if not user and '@' in username_or_email:
                user_obj = User.objects.filter(email__iexact=username_or_email).first()
                if user_obj:
                    user = authenticate(request, username=user_obj.username, password=password)

            if user is not None:
                old_session_key = request.session.session_key
                login(request, user)
                if not remember_me:
                    request.session.set_expiry(0)  # Expires when browser closes
                else:
                    request.session.set_expiry(1209600)  # 2 weeks

                # Merge or associate cart
                _merge_session_cart(request, old_session_key)

                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                return redirect(next_url)
            else:
                messages.error(request, "Invalid username/email or password. Please try again.")
    else:
        form = UserLoginForm()

    return render(request, 'login.html', {'form': form, 'next': next_url})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('home')


@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            # Update User fields
            request.user.first_name = form.cleaned_data.get('first_name', '')
            request.user.last_name = form.cleaned_data.get('last_name', '')
            request.user.email = form.cleaned_data.get('email', '')
            request.user.save()

            form.save()
            messages.success(request, "Your profile information has been updated.")
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile, user=request.user)

    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]

    context = {
        'form': form,
        'user_form': form,
        'profile_form': form,
        'profile': profile,
        'recent_orders': recent_orders,
    }
    return render(request, 'profile.html', context)


@login_required
def checkout_view(request):
    cart = _get_or_create_cart(request)
    cart_items = cart.items.select_related('product').all()

    if not cart_items.exists():
        messages.warning(request, "Your shopping cart is empty. Please add items before checking out.")
        return redirect('products')

    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Crucial Server-Side Validation:
            # 1. Recalculate stock and prices strictly in the database transaction
            # 2. Never trust client submitted amounts
            try:
                with transaction.atomic():
                    # Check stock availability for all items
                    for item in cart_items:
                        # Lock row for update
                        product = Product.objects.select_for_update().get(id=item.product.id)
                        if not product.available or product.stock_quantity < item.quantity:
                            messages.error(
                                request,
                                f"Insufficient stock for '{product.name}'. Only {product.stock_quantity} available."
                            )
                            return redirect('cart')

                    # Compute authoritative server totals
                    computed_subtotal = Decimal('0.00')
                    for item in cart_items:
                        item_unit_price = item.product.get_effective_price()
                        computed_subtotal += item_unit_price * item.quantity

                    shipping_cost = Decimal('0.00') if computed_subtotal >= Decimal('75.00') else Decimal('9.99')
                    computed_total = computed_subtotal + shipping_cost

                    # Create Order
                    order = form.save(commit=False)
                    order.user = request.user
                    order.subtotal = computed_subtotal
                    order.shipping_cost = shipping_cost
                    order.total = computed_total
                    order.order_status = Order.STATUS_PENDING
                    order.payment_method = form.cleaned_data.get('payment_method', Order.PAYMENT_COD)
                    order.save()

                    # Create OrderItems snapshots and reduce stock
                    for item in cart_items:
                        product = Product.objects.select_for_update().get(id=item.product.id)
                        unit_price = product.get_effective_price()
                        item_subtotal = unit_price * item.quantity

                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            product_name=product.name,
                            price=unit_price,
                            quantity=item.quantity,
                            subtotal=item_subtotal
                        )

                        # Decrement stock
                        product.stock_quantity -= item.quantity
                        if product.stock_quantity <= 0:
                            product.stock_quantity = 0
                        product.save()

                    # Clear the user's cart
                    cart.items.all().delete()

                    # Optionally update profile address if empty
                    if not profile.phone:
                        profile.phone = order.phone
                    if not profile.address:
                        profile.address = order.address
                    if not profile.city:
                        profile.city = order.city
                    if not profile.postal_code:
                        profile.postal_code = order.postal_code
                    profile.save()

                    messages.success(
                        request,
                        f"Order #{order.order_number} has been placed successfully! Thank you for shopping with ShopEase."
                    )
                    return redirect('order_detail', order_number=order.order_number)

            except Exception as e:
                messages.error(request, f"An error occurred while processing your order: {str(e)}")
                return redirect('checkout')
    else:
        # Pre-populate form with user profile information
        initial_data = {
            'full_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
            'email': request.user.email,
            'phone': profile.phone,
            'address': profile.address,
            'city': profile.city,
            'postal_code': profile.postal_code,
            'payment_method': Order.PAYMENT_COD,
        }
        form = CheckoutForm(initial=initial_data)

    context = {
        'form': form,
        'cart': cart,
        'cart_items': cart_items,
        'items': cart_items,
        'subtotal': cart.get_subtotal(),
        'shipping_cost': cart.get_shipping_cost(),
        'total': cart.get_total(),
    }
    return render(request, 'checkout.html', context)


@login_required
def orders_view(request):
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders.html', {'orders': user_orders})


@login_required
def order_detail_view(request, order_number):
    # Strict security authorization check: users can only view their own orders
    if request.user.is_staff:
        order = get_object_or_404(Order, order_number=order_number)
    else:
        order = get_object_or_404(Order, order_number=order_number, user=request.user)

    order_items = order.items.select_related('product').all()

    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'order_detail.html', context)


@login_required
@require_POST
def cancel_order_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)

    if not order.can_cancel():
        messages.error(request, f"Order #{order.order_number} cannot be cancelled as it is already {order.order_status}.")
        return redirect('order_detail', order_number=order.order_number)

    with transaction.atomic():
        # Restore stock for each item
        for item in order.items.all():
            if item.product:
                product = Product.objects.select_for_update().get(id=item.product.id)
                product.stock_quantity += item.quantity
                if product.stock_quantity > 0:
                    product.available = True
                product.save()

        order.order_status = Order.STATUS_CANCELLED
        order.save()

    messages.info(request, f"Order #{order.order_number} has been cancelled and stock has been restored.")
    return redirect('order_detail', order_number=order.order_number)


def about_view(request):
    return render(request, 'about.html')


def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if name and email and message:
            messages.success(
                request,
                f"Thank you, {name}! Your message regarding '{subject or 'general inquiry'}' has been received. Our team will contact you at {email}."
            )
            return redirect('contact')
        else:
            messages.error(request, "Please fill in all required fields.")

    return render(request, 'contact.html')


def handler404(request, exception=None):
    return render(request, '404.html', status=404)


def handler500(request):
    return render(request, '500.html', status=500)
