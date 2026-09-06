from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from store.models import Category, Product, Cart, CartItem, Order, OrderItem, UserProfile


class ShopEaseTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Create category
        self.category = Category.objects.create(
            name='Test Electronics',
            slug='test-electronics',
            description='Test category description'
        )

        # Create products
        self.product1 = Product.objects.create(
            category=self.category,
            name='Test Wireless Speaker',
            slug='test-wireless-speaker',
            description='High quality sound with bluetooth',
            price=Decimal('100.00'),
            discount_price=Decimal('80.00'),
            stock_quantity=10,
            available=True
        )

        self.product_low_stock = Product.objects.create(
            category=self.category,
            name='Limited Edition Watch',
            slug='limited-edition-watch',
            description='Exclusive timepiece',
            price=Decimal('200.00'),
            stock_quantity=2,
            available=True
        )

        self.product_out_of_stock = Product.objects.create(
            category=self.category,
            name='Sold Out Camera',
            slug='sold-out-camera',
            description='Currently unavailable',
            price=Decimal('300.00'),
            stock_quantity=0,
            available=True
        )

        # Create users
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='Password123!',
            first_name='Alice',
            last_name='Smith'
        )
        UserProfile.objects.create(
            user=self.user1,
            phone='1234567890',
            address='123 First St',
            city='Boston',
            postal_code='02101'
        )

        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='Password123!',
            first_name='Bob',
            last_name='Jones'
        )
        UserProfile.objects.create(
            user=self.user2,
            phone='9876543210',
            address='456 Second Ave',
            city='Chicago',
            postal_code='60601'
        )


class AuthenticationTests(ShopEaseTestCase):
    def test_user_registration_success(self):
        response = self.client.post(reverse('register'), {
            'full_name': 'Charlie Brown',
            'username': 'charlie',
            'email': 'charlie@example.com',
            'password': 'Password123!',
            'confirm_password': 'Password123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='charlie').exists())
        user = User.objects.get(username='charlie')
        self.assertEqual(user.first_name, 'Charlie')
        self.assertEqual(user.last_name, 'Brown')
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_user_registration_duplicate_username(self):
        response = self.client.post(reverse('register'), {
            'full_name': 'Duplicate User',
            'username': 'user1',
            'email': 'different@example.com',
            'password': 'Password123!',
            'confirm_password': 'Password123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'username', 'This username is already taken. Please choose another.')

    def test_user_registration_password_mismatch(self):
        response = self.client.post(reverse('register'), {
            'full_name': 'Mismatch User',
            'username': 'mismatch',
            'email': 'mismatch@example.com',
            'password': 'Password123!',
            'confirm_password': 'DifferentPassword!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'confirm_password', 'Passwords do not match.')

    def test_user_login_valid(self):
        response = self.client.post(reverse('login'), {
            'username': 'user1',
            'password': 'Password123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user1.pk)

    def test_user_login_invalid(self):
        response = self.client.post(reverse('login'), {
            'username': 'user1',
            'password': 'WrongPassword',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_user_logout(self):
        self.client.login(username='user1', password='Password123!')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('_auth_user_id', self.client.session)


class ProductTests(ShopEaseTestCase):
    def test_product_list_view(self):
        response = self.client.get(reverse('products'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Wireless Speaker')
        self.assertContains(response, 'Limited Edition Watch')

    def test_product_detail_view(self):
        response = self.client.get(reverse('product_detail', args=[self.product1.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Wireless Speaker')
        self.assertContains(response, 'High quality sound with bluetooth')

    def test_invalid_product_detail_404(self):
        response = self.client.get(reverse('product_detail', args=['non-existent-product-slug']))
        self.assertEqual(response.status_code, 404)

    def test_product_search(self):
        response = self.client.get(reverse('products') + '?q=Speaker')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Wireless Speaker')
        self.assertNotContains(response, 'Limited Edition Watch')

    def test_product_filter_category(self):
        other_cat = Category.objects.create(name='Clothing', slug='clothing')
        shirt = Product.objects.create(
            category=other_cat,
            name='Linen Shirt',
            slug='linen-shirt',
            description='Cool linen',
            price=Decimal('45.00'),
            stock_quantity=5,
            available=True
        )
        response = self.client.get(reverse('products_by_category', args=['clothing']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Linen Shirt')
        self.assertNotContains(response, 'Test Wireless Speaker')


class CartTests(ShopEaseTestCase):
    def test_add_product_to_cart(self):
        response = self.client.post(reverse('add_to_cart', args=[self.product1.id]), {'quantity': 2})
        self.assertEqual(response.status_code, 302)

        session_key = self.client.session.session_key
        cart = Cart.objects.get(session_key=session_key)
        self.assertEqual(cart.get_total_items(), 2)

        item = cart.items.first()
        self.assertEqual(item.product, self.product1)
        self.assertEqual(item.quantity, 2)
        # Unit price should be discounted $80.00
        self.assertEqual(item.get_unit_price(), Decimal('80.00'))
        self.assertEqual(item.get_subtotal(), Decimal('160.00'))

    def test_prevent_quantity_above_stock(self):
        # product_low_stock only has 2 in stock
        response = self.client.post(
            reverse('add_to_cart', args=[self.product_low_stock.id]),
            {'quantity': 10}
        )
        self.assertEqual(response.status_code, 302)

        session_key = self.client.session.session_key
        cart = Cart.objects.get(session_key=session_key)
        item = cart.items.get(product=self.product_low_stock)
        # Should be capped at maximum available stock (2)
        self.assertEqual(item.quantity, 2)

    def test_update_cart_quantity(self):
        self.client.post(reverse('add_to_cart', args=[self.product1.id]), {'quantity': 1})
        session_key = self.client.session.session_key
        cart = Cart.objects.get(session_key=session_key)
        item = cart.items.first()

        # Increase quantity
        self.client.post(reverse('update_cart', args=[item.id]), {'action': 'increase'})
        item.refresh_from_db()
        self.assertEqual(item.quantity, 2)

        # Decrease quantity
        self.client.post(reverse('update_cart', args=[item.id]), {'action': 'decrease'})
        item.refresh_from_db()
        self.assertEqual(item.quantity, 1)

    def test_remove_product_from_cart(self):
        self.client.post(reverse('add_to_cart', args=[self.product1.id]), {'quantity': 1})
        session_key = self.client.session.session_key
        cart = Cart.objects.get(session_key=session_key)
        item = cart.items.first()

        response = self.client.get(reverse('remove_from_cart', args=[item.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(cart.items.count(), 0)


class OrderAndSecurityTests(ShopEaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username='user1', password='Password123!')
        # Add item to user1's cart
        self.client.post(reverse('add_to_cart', args=[self.product1.id]), {'quantity': 2})

    def test_checkout_requires_authentication(self):
        unauth_client = Client()
        response = unauth_client.get(reverse('checkout'))
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_order_creation_workflow(self):
        initial_stock = self.product1.stock_quantity  # 10
        response = self.client.post(reverse('checkout'), {
            'full_name': 'Alice Smith',
            'email': 'user1@example.com',
            'phone': '1234567890',
            'address': '123 First St',
            'city': 'Boston',
            'postal_code': '02101',
            'payment_method': Order.PAYMENT_COD,
        })
        self.assertEqual(response.status_code, 302)

        # Order created
        order = Order.objects.filter(user=self.user1).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.full_name, 'Alice Smith')
        self.assertEqual(order.order_status, Order.STATUS_PENDING)

        # Server-side price calculation: 2 * $80.00 = $160.00 (>= $75 free shipping)
        self.assertEqual(order.subtotal, Decimal('160.00'))
        self.assertEqual(order.shipping_cost, Decimal('0.00'))
        self.assertEqual(order.total, Decimal('160.00'))

        # Order item snapshot verified
        order_item = order.items.first()
        self.assertEqual(order_item.product_name, 'Test Wireless Speaker')
        self.assertEqual(order_item.price, Decimal('80.00'))
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.subtotal, Decimal('160.00'))

        # Stock reduced correctly
        self.product1.refresh_from_db()
        self.assertEqual(self.product1.stock_quantity, initial_stock - 2)

        # Cart cleared
        cart = Cart.objects.get(user=self.user1)
        self.assertEqual(cart.items.count(), 0)

    def test_unauthorized_order_access_forbidden(self):
        # Create order for user1
        order = Order.objects.create(
            user=self.user1,
            order_number='SE-PRIVATE999',
            full_name='Alice Smith',
            email='user1@example.com',
            phone='1234567890',
            address='123 First St',
            city='Boston',
            postal_code='02101',
            subtotal=Decimal('100.00'),
            shipping_cost=Decimal('0.00'),
            total=Decimal('100.00'),
            payment_method=Order.PAYMENT_COD,
            order_status=Order.STATUS_CONFIRMED
        )

        # Now login as user2 and attempt to access user1's order
        client_user2 = Client()
        client_user2.login(username='user2', password='Password123!')

        response = client_user2.get(reverse('order_detail', args=[order.order_number]))
        # User2 must NOT be able to view user1's order - expect 404 (or forbidden)
        self.assertEqual(response.status_code, 404)

    def test_user_can_view_own_order(self):
        order = Order.objects.create(
            user=self.user1,
            order_number='SE-OWN123',
            full_name='Alice Smith',
            email='user1@example.com',
            phone='1234567890',
            address='123 First St',
            city='Boston',
            postal_code='02101',
            subtotal=Decimal('100.00'),
            shipping_cost=Decimal('0.00'),
            total=Decimal('100.00'),
            payment_method=Order.PAYMENT_COD,
            order_status=Order.STATUS_CONFIRMED
        )
        response = self.client.get(reverse('order_detail', args=[order.order_number]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SE-OWN123')
