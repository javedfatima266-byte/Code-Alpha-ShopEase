import os
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from store.models import Category, Product, Order, OrderItem, Cart, CartItem, UserProfile


class FullE2EUserJourneyAuditTest(TestCase):
    """
    Comprehensive End-to-End User Journey Audit:
    Home -> Products -> Search -> Filter -> Product Details -> Add to Cart
    -> Change Quantity -> Register -> Checkout -> Place Order -> Order Confirmation
    -> My Orders -> Order Details -> Logout -> Login Again -> Verify Order History
    """
    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        self.category = Category.objects.create(
            name='Audio & Sound',
            slug='audio-sound',
            description='Headphones, speakers, soundbars'
        )
        self.product = Product.objects.create(
            category=self.category,
            name='Studio Wireless Headphones',
            slug='studio-wireless-headphones',
            description='Noise cancelling pro headphones',
            price=Decimal('120.00'),
            discount_price=Decimal('99.00'),
            stock_quantity=15,
            available=True
        )

    def test_complete_e2e_user_journey(self):
        # 1. Home
        res = self.client.get(reverse('home'))
        self.assertEqual(res.status_code, 200)

        # 2. Products
        res = self.client.get(reverse('products'))
        self.assertEqual(res.status_code, 200)

        # 3. Search
        res = self.client.get(reverse('products') + '?q=headphones')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Studio Wireless Headphones')

        # 4. Filter
        res = self.client.get(reverse('products') + '?sort=price_asc&availability=in_stock')
        self.assertEqual(res.status_code, 200)

        # 5. Product Details
        initial_stock = self.product.stock_quantity
        res = self.client.get(reverse('product_detail', args=[self.product.slug]))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Studio Wireless Headphones')

        # 6. Add to Cart (Guest session)
        res = self.client.post(reverse('add_to_cart', args=[self.product.id]), {'quantity': 2}, follow=True)
        self.assertEqual(res.status_code, 200)
        session_key = self.client.session.session_key
        guest_cart = Cart.objects.get(session_key=session_key)
        item = guest_cart.items.get(product=self.product)
        self.assertEqual(item.quantity, 2)

        # 7. Change Quantity in Cart (Increase then decrease)
        res = self.client.post(reverse('update_cart', args=[item.id]), {'action': 'increase'}, follow=True)
        self.assertEqual(res.status_code, 200)
        item.refresh_from_db()
        self.assertEqual(item.quantity, 3)

        res = self.client.post(reverse('update_cart', args=[item.id]), {'action': 'decrease'}, follow=True)
        self.assertEqual(res.status_code, 200)
        item.refresh_from_db()
        self.assertEqual(item.quantity, 2)

        # 8. Register Account & verify Cart Merge
        test_username = 'journey_auditor'
        test_email = 'auditor@example.com'
        test_pwd = 'AuditorSecure123!'

        res = self.client.post(reverse('register'), {
            'full_name': 'Auditor Person',
            'username': test_username,
            'email': test_email,
            'password': test_pwd,
            'confirm_password': test_pwd,
        }, follow=True)
        self.assertEqual(res.status_code, 200)
        user = User.objects.get(username=test_username)

        # Verify cart was merged to authenticated user
        user_cart = Cart.objects.get(user=user)
        self.assertTrue(user_cart.items.filter(product=self.product, quantity=2).exists())

        # 9. Checkout Page
        res = self.client.get(reverse('checkout'))
        self.assertEqual(res.status_code, 200)

        # 10. Place Order
        res = self.client.post(reverse('checkout'), {
            'full_name': 'Auditor Person',
            'email': test_email,
            'phone': '+1 (555) 019-2834',
            'address': '100 Audit Boulevard, Floor 3',
            'city': 'San Francisco',
            'postal_code': '94105',
            'payment_method': Order.PAYMENT_COD,
        }, follow=True)
        self.assertEqual(res.status_code, 200)

        # 11. Order Confirmation & Calculations
        order = Order.objects.filter(user=user).first()
        self.assertIsNotNone(order)
        # Authoritative server-side calculations:
        # Unit price is discount $99.00 * 2 = $198.00 (subtotal >= $75 -> free shipping)
        self.assertEqual(order.subtotal, Decimal('198.00'))
        self.assertEqual(order.shipping_cost, Decimal('0.00'))
        self.assertEqual(order.total, Decimal('198.00'))

        # Stock decrease verified
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, initial_stock - 2)

        # Cart cleared verified
        user_cart.refresh_from_db()
        self.assertEqual(user_cart.items.count(), 0)

        # 12. My Orders View
        res = self.client.get(reverse('orders'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, order.order_number)

        # 13. Order Details View
        res = self.client.get(reverse('order_detail', args=[order.order_number]))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, order.order_number)

        # 14. Logout
        res = self.client.get(reverse('logout'), follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

        # 15. Login Again
        res = self.client.post(reverse('login'), {
            'username': test_username,
            'password': test_pwd,
        }, follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(int(self.client.session['_auth_user_id']), user.id)

        # 16. Verify Order History after re-login
        res = self.client.get(reverse('orders'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, order.order_number)

        # Order Details accessible after re-login
        res = self.client.get(reverse('order_detail', args=[order.order_number]))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, order.order_number)

    def test_empty_cart_checkout_redirects(self):
        user = User.objects.create_user(username='emptycartuser', password='Password123!')
        self.client.force_login(user)
        # Ensure cart is empty
        Cart.objects.filter(user=user).delete()
        res = self.client.get(reverse('checkout'), follow=True)
        # Should redirect to products with a friendly warning message
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'shopping cart is empty')

    def test_invalid_urls_return_404(self):
        res = self.client.get('/definitely-a-non-existent-url-slug-9999/')
        self.assertEqual(res.status_code, 404)

    def test_out_of_stock_product_add_fails_gracefully(self):
        sold_out = Product.objects.create(
            category=self.category,
            name='Vintage Gramophone',
            slug='vintage-gramophone',
            description='Out of stock collectable',
            price=Decimal('500.00'),
            stock_quantity=0,
            available=True
        )
        res = self.client.post(reverse('add_to_cart', args=[sold_out.id]), {'quantity': 1}, follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'out of stock')

    def test_order_cancellation_restores_inventory(self):
        user = User.objects.create_user(username='canceluser', password='Password123!')
        self.client.force_login(user)
        initial_stock = self.product.stock_quantity

        # Create an order
        order = Order.objects.create(
            user=user,
            order_number='SE-CANCELTEST1',
            full_name='Cancel User',
            email='cancel@example.com',
            phone='1234567890',
            address='123 Street',
            city='Boston',
            postal_code='02101',
            subtotal=Decimal('99.00'),
            shipping_cost=Decimal('0.00'),
            total=Decimal('99.00'),
            payment_method=Order.PAYMENT_COD,
            order_status=Order.STATUS_PENDING
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            product_name=self.product.name,
            price=Decimal('99.00'),
            quantity=2,
            subtotal=Decimal('198.00')
        )
        # Deduct stock as order was placed
        self.product.stock_quantity -= 2
        self.product.save()

        # Cancel the order
        res = self.client.post(reverse('cancel_order', args=[order.order_number]), follow=True)
        self.assertEqual(res.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.order_status, Order.STATUS_CANCELLED)

        # Inventory must be restored
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, initial_stock)

