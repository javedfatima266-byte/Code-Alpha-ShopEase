from .models import Cart, Category

def store_context(request):
    """Context processor providing cart item count and categories across all templates."""
    cart_count = 0
    try:
        cart = None
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        elif request.session.session_key:
            cart = Cart.objects.filter(session_key=request.session.session_key).first()

        if cart:
            cart_count = cart.get_total_items()
    except Exception:
        cart_count = 0

    try:
        categories = Category.objects.all()[:8]
    except Exception:
        categories = []

    return {
        'cart_count': cart_count,
        'cart_item_count': cart_count,
        'nav_categories': categories,
        'STORE_NAME': 'ShopEase',
    }
