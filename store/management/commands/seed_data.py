from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import Category, Product, UserProfile, Order, OrderItem


class Command(BaseCommand):
    help = 'Seeds initial ShopEase sample data: categories, products, admin, and demo user.'

    def handle(self, *args, **options):
        self.stdout.write("Seeding ShopEase database...")

        # 1. Create Superuser (Admin)
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@shopease.com',
                'first_name': 'ShopEase',
                'last_name': 'Administrator',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            UserProfile.objects.get_or_create(user=admin_user, defaults={'city': 'San Francisco', 'phone': '+1 (555) 100-2000'})
            self.stdout.write(self.style.SUCCESS("Created superuser 'admin' (password: admin123)"))
        else:
            self.stdout.write("Superuser 'admin' already exists.")

        # 2. Create Demo Customer
        demo_user, created = User.objects.get_or_create(
            username='intern_demo',
            defaults={
                'email': 'demo@shopease.com',
                'first_name': 'Alex',
                'last_name': 'Morgan',
            }
        )
        if created:
            demo_user.set_password('password123')
            demo_user.save()
            UserProfile.objects.get_or_create(
                user=demo_user,
                defaults={
                    'phone': '+1 (555) 345-6789',
                    'address': '742 Evergreen Terrace, Suite 4B',
                    'city': 'Springfield',
                    'postal_code': '97477',
                }
            )
            self.stdout.write(self.style.SUCCESS("Created demo customer 'intern_demo' (password: password123)"))
        else:
            self.stdout.write("Demo customer 'intern_demo' already exists.")

        # 3. Create Categories
        categories_data = [
            {
                'name': 'Electronics',
                'slug': 'electronics',
                'icon': 'cpu',
                'description': 'High-performance audio, smart mobile gear, personal computing, and daily tech essentials.'
            },
            {
                'name': 'Fashion',
                'slug': 'fashion',
                'icon': 'shirt',
                'description': 'Contemporary apparel, seasonal streetwear, tailored outerwear, and everyday breathable fabrics.'
            },
            {
                'name': 'Home & Living',
                'slug': 'home-living',
                'icon': 'home',
                'description': 'Ergonomic furniture, ambient ceramic lighting, artisan kitchenware, and modern interior decor.'
            },
            {
                'name': 'Accessories',
                'slug': 'accessories',
                'icon': 'watch',
                'description': 'Handcrafted leather wallets, precision mechanical chronographs, eyewear, and water-repellent packs.'
            },
            {
                'name': 'Beauty & Wellness',
                'slug': 'beauty-wellness',
                'icon': 'sparkles',
                'description': 'Botanical skincare serums, natural essential oils, restorative bath infusions, and wellness tools.'
            },
        ]

        cat_objs = {}
        for cat in categories_data:
            obj, _ = Category.objects.get_or_create(
                slug=cat['slug'],
                defaults={
                    'name': cat['name'],
                    'icon': cat['icon'],
                    'description': cat['description'],
                }
            )
            cat_objs[cat['slug']] = obj
        self.stdout.write(self.style.SUCCESS(f"Categories verified ({len(cat_objs)} total)."))

        # 4. Create 18 Realistic Products
        products_data = [
            # Electronics
            {
                'category': 'electronics',
                'name': 'AeroSound Pro Wireless Headphones',
                'slug': 'aerosound-pro-wireless-headphones',
                'description': 'Engineered with active hybrid noise cancellation, 40mm titanium diaphragm drivers, and 42-hour battery life. Features seamless multi-device Bluetooth 5.3 pairing, breathable memory-foam ear cushions, and ultra-low latency audio streaming.',
                'price': Decimal('189.99'),
                'discount_price': Decimal('149.99'),
                'stock_quantity': 24,
                'available': True,
                'rating': Decimal('4.85'),
                'review_count': 64,
                'is_featured': True,
                'image_url': '/static/images/products/headphones.svg',
            },
            {
                'category': 'electronics',
                'name': 'PulseFit Chroma Smartwatch 2',
                'slug': 'pulsefit-chroma-smartwatch-2',
                'description': 'Sleek aerospace-grade aluminum casing with an always-on 1.78" AMOLED curved display. Delivers 24/7 heart-rate monitoring, SpO2 tracking, sleep stages analysis, and 50-meter water resistance with 10-day battery stamina.',
                'price': Decimal('129.50'),
                'discount_price': None,
                'stock_quantity': 18,
                'available': True,
                'rating': Decimal('4.70'),
                'review_count': 42,
                'is_featured': True,
                'image_url': '/static/images/products/smartwatch.svg',
            },
            {
                'category': 'electronics',
                'name': 'NovaPod SoundBar Studio',
                'slug': 'novapod-soundbar-studio',
                'description': 'Immersive 3.1 channel room-filling audio featuring Dolby Atmos spatial decoding, integrated dual subwoofers, HDMI eARC support, and optical inputs designed to elevate home theater audio.',
                'price': Decimal('229.00'),
                'discount_price': Decimal('199.00'),
                'stock_quantity': 12,
                'available': True,
                'rating': Decimal('4.65'),
                'review_count': 29,
                'is_featured': False,
                'image_url': '/static/images/products/soundbar.svg',
            },
            {
                'category': 'electronics',
                'name': 'ApexMech 75% Mechanical Keyboard',
                'slug': 'apexmech-mechanical-keyboard',
                'description': 'Compact 75% layout with hot-swappable tactile mechanical switches, sound-dampening silicone gaskets, customizable per-key RGB backlighting, and CNC-machined anodized aluminum top plate.',
                'price': Decimal('115.00'),
                'discount_price': Decimal('98.00'),
                'stock_quantity': 15,
                'available': True,
                'rating': Decimal('4.90'),
                'review_count': 53,
                'is_featured': True,
                'image_url': '/static/images/products/keyboard.svg',
            },

            # Fashion
            {
                'category': 'fashion',
                'name': 'Merino Wool Minimalist Crewneck',
                'slug': 'merino-wool-minimalist-crewneck',
                'description': 'Crafted from 100% superfine Australian Merino wool. Naturally thermoregulating, odor-resistant, and pill-resistant with ribbed cuffs and hem. Designed for timeless layering and everyday refinement.',
                'price': Decimal('89.00'),
                'discount_price': Decimal('74.50'),
                'stock_quantity': 30,
                'available': True,
                'rating': Decimal('4.75'),
                'review_count': 38,
                'is_featured': True,
                'image_url': '/static/images/products/sweater.svg',
            },
            {
                'category': 'fashion',
                'name': 'UrbanTech Water-Resistant Parka',
                'slug': 'urbantech-water-resistant-parka',
                'description': 'All-weather technical shell jacket with a sealed seam 3-layer breathable membrane, storm-flap dual front zipper, fleece-lined handwarmer pockets, and adjustable hood for metropolitan commutes.',
                'price': Decimal('165.00'),
                'discount_price': None,
                'stock_quantity': 14,
                'available': True,
                'rating': Decimal('4.80'),
                'review_count': 26,
                'is_featured': True,
                'image_url': '/static/images/products/jacket.svg',
            },
            {
                'category': 'fashion',
                'name': 'Tailored Slim Chino Trousers',
                'slug': 'tailored-slim-chino-trousers',
                'description': 'Premium 98% combed cotton with 2% elastane flex stretch. Features a comfortable mid-rise cut, reinforced pockets, and internal waistband gripper tailored for office and smart-casual weekends.',
                'price': Decimal('58.00'),
                'discount_price': Decimal('49.00'),
                'stock_quantity': 22,
                'available': True,
                'rating': Decimal('4.60'),
                'review_count': 19,
                'is_featured': False,
                'image_url': '/static/images/products/chinos.svg',
            },
            {
                'category': 'fashion',
                'name': 'Strata Canvas High-Top Sneakers',
                'slug': 'strata-canvas-high-top-sneakers',
                'description': 'Heavyweight organic cotton duck canvas upper with vulcanized natural gum rubber outsoles and cushioned OrthoLite insoles for vintage aesthetics and all-day shock absorption.',
                'price': Decimal('75.00'),
                'discount_price': None,
                'stock_quantity': 19,
                'available': True,
                'rating': Decimal('4.70'),
                'review_count': 31,
                'is_featured': False,
                'image_url': '/static/images/products/sneakers.svg',
            },

            # Home & Living
            {
                'category': 'home-living',
                'name': 'Artisan Hand-Poured Ceramic Mug Set',
                'slug': 'artisan-ceramic-mug-set',
                'description': 'Set of 4 matte-glazed stoneware mugs hand-finished with organic speckling. Microwave, dishwasher, and food safe with generous 14oz capacity and ergonomic wide-loop handles.',
                'price': Decimal('42.00'),
                'discount_price': Decimal('35.00'),
                'stock_quantity': 25,
                'available': True,
                'rating': Decimal('4.90'),
                'review_count': 47,
                'is_featured': True,
                'image_url': '/static/images/products/mug.svg',
            },
            {
                'category': 'home-living',
                'name': 'Nordic Dimmable Bedside Lamp',
                'slug': 'nordic-dimmable-bedside-lamp',
                'description': 'Solid natural ash wood base paired with a spun aluminum dome shade. Features continuous touch-dimming control, warm 2700K ambient LED glow, and integrated USB-C charging outlet.',
                'price': Decimal('68.00'),
                'discount_price': None,
                'stock_quantity': 16,
                'available': True,
                'rating': Decimal('4.80'),
                'review_count': 33,
                'is_featured': True,
                'image_url': '/static/images/products/lamp.svg',
            },
            {
                'category': 'home-living',
                'name': 'Lumina Ultrasonic Mist Diffuser',
                'slug': 'lumina-ultrasonic-mist-diffuser',
                'description': 'Whisper-quiet 350ml aromatherapy diffuser with handcrafted textured ceramic exterior, warm ambient breath light mode, and safety auto-shutoff when water level runs dry.',
                'price': Decimal('49.99'),
                'discount_price': Decimal('39.99'),
                'stock_quantity': 28,
                'available': True,
                'rating': Decimal('4.65'),
                'review_count': 55,
                'is_featured': False,
                'image_url': '/static/images/products/diffuser.svg',
            },
            {
                'category': 'home-living',
                'name': 'Pure French Flax Linen Throw Blanket',
                'slug': 'french-flax-linen-throw-blanket',
                'description': 'Woven from 100% stone-washed certified French flax. Soft, textured, and breathable throughout every season with delicate eyelash fringe edges in neutral stone grey.',
                'price': Decimal('85.00'),
                'discount_price': Decimal('72.00'),
                'stock_quantity': 11,
                'available': True,
                'rating': Decimal('4.70'),
                'review_count': 21,
                'is_featured': False,
                'image_url': '/static/images/products/blanket.svg',
            },

            # Accessories
            {
                'category': 'accessories',
                'name': 'Vanguard Full-Grain Leather Bi-Fold',
                'slug': 'vanguard-full-grain-leather-wallet',
                'description': 'Vegetable-tanned full-grain leather wallet with integrated RFID-blocking inner lining, 8 dedicated card slots, cash divider, and compact slim pocket profile that ages with a rich patina.',
                'price': Decimal('55.00'),
                'discount_price': Decimal('44.00'),
                'stock_quantity': 35,
                'available': True,
                'rating': Decimal('4.85'),
                'review_count': 68,
                'is_featured': True,
                'image_url': '/static/images/products/wallet.svg',
            },
            {
                'category': 'accessories',
                'name': 'AeroTransit Commuter Backpack 22L',
                'slug': 'aerotransit-commuter-backpack',
                'description': 'Built from recycled Cordura ballistic nylon with weatherproof YKK AquaGuard zips. Dedicated padded 16" laptop chamber, quick-access passport pocket, and luggage pass-through trolley sleeve.',
                'price': Decimal('119.00'),
                'discount_price': Decimal('99.00'),
                'stock_quantity': 20,
                'available': True,
                'rating': Decimal('4.90'),
                'review_count': 74,
                'is_featured': True,
                'image_url': '/static/images/products/backpack.svg',
            },
            {
                'category': 'accessories',
                'name': 'Chronos Classic Bauhaus Watch',
                'slug': 'chronos-classic-bauhaus-watch',
                'description': 'Minimalist 38mm stainless steel dress watch with domed sapphire crystal, Swiss Ronda quartz movement, clean white sub-dial, and quick-release Italian calfskin leather strap.',
                'price': Decimal('145.00'),
                'discount_price': None,
                'stock_quantity': 10,
                'available': True,
                'rating': Decimal('4.75'),
                'review_count': 36,
                'is_featured': False,
                'image_url': '/static/images/products/classic-watch.svg',
            },

            # Beauty & Wellness
            {
                'category': 'beauty-wellness',
                'name': 'Botanical Radiance Vitamin C Serum',
                'slug': 'botanical-radiance-vitamin-c-serum',
                'description': 'Potent 15% ethyl ascorbic acid stabilized with ferulic acid, hyaluronic acid, and organic rosehip extract. Formulated to brighten skin tone, support collagen, and combat oxidative stress.',
                'price': Decimal('38.00'),
                'discount_price': Decimal('32.00'),
                'stock_quantity': 40,
                'available': True,
                'rating': Decimal('4.90'),
                'review_count': 92,
                'is_featured': True,
                'image_url': '/static/images/products/serum.svg',
            },
            {
                'category': 'beauty-wellness',
                'name': 'Himalayan Pink Salt Bath Soak 500g',
                'slug': 'himalayan-pink-salt-bath-soak',
                'description': 'Pure mineral-rich Himalayan pink crystal salts infused with cold-pressed lavender, bergamot, and sweet almond oils to relieve muscle fatigue and nourish skin after demanding days.',
                'price': Decimal('24.00'),
                'discount_price': None,
                'stock_quantity': 26,
                'available': True,
                'rating': Decimal('4.80'),
                'review_count': 41,
                'is_featured': False,
                'image_url': '/static/images/products/bath-salt.svg',
            },
            {
                'category': 'beauty-wellness',
                'name': 'Rose Quartz Facial Sculpting Roller',
                'slug': 'rose-quartz-facial-roller',
                'description': 'Handcrafted dual-ended roller carved from genuine natural Brazilian rose quartz. Aids lymphatic drainage, eases facial tension, and enhances absorption of favorite serums and moisturizers.',
                'price': Decimal('28.00'),
                'discount_price': Decimal('22.50'),
                'stock_quantity': 32,
                'available': True,
                'rating': Decimal('4.65'),
                'review_count': 27,
                'is_featured': False,
                'image_url': '/static/images/products/roller.svg',
            },
        ]

        for p_data in products_data:
            cat_obj = cat_objs[p_data['category']]
            Product.objects.update_or_create(
                slug=p_data['slug'],
                defaults={
                    'category': cat_obj,
                    'name': p_data['name'],
                    'description': p_data['description'],
                    'price': p_data['price'],
                    'discount_price': p_data['discount_price'],
                    'stock_quantity': p_data['stock_quantity'],
                    'available': p_data['available'],
                    'rating': p_data['rating'],
                    'review_count': p_data['review_count'],
                    'is_featured': p_data['is_featured'],
                    'image_url': p_data['image_url'],
                }
            )
        self.stdout.write(self.style.SUCCESS(f"Products seeded successfully ({len(products_data)} total)."))

        # 5. Create a sample initial order for the demo user
        if not Order.objects.filter(user=demo_user).exists():
            p1 = Product.objects.get(slug='aerosound-pro-wireless-headphones')
            p2 = Product.objects.get(slug='artisan-ceramic-mug-set')

            unit1 = p1.get_effective_price()
            unit2 = p2.get_effective_price()
            subtotal = unit1 + (unit2 * 2)
            shipping = Decimal('0.00') if subtotal >= Decimal('75.00') else Decimal('9.99')
            total = subtotal + shipping

            sample_order = Order.objects.create(
                user=demo_user,
                order_number='SE-DEMO1001',
                full_name='Alex Morgan',
                email='demo@shopease.com',
                phone='+1 (555) 345-6789',
                address='742 Evergreen Terrace, Suite 4B',
                city='Springfield',
                postal_code='97477',
                subtotal=subtotal,
                shipping_cost=shipping,
                total=total,
                payment_method=Order.PAYMENT_COD,
                order_status=Order.STATUS_CONFIRMED
            )

            OrderItem.objects.create(
                order=sample_order,
                product=p1,
                product_name=p1.name,
                price=unit1,
                quantity=1,
                subtotal=unit1
            )
            OrderItem.objects.create(
                order=sample_order,
                product=p2,
                product_name=p2.name,
                price=unit2,
                quantity=2,
                subtotal=unit2 * 2
            )
            self.stdout.write(self.style.SUCCESS("Created sample confirmed order for demo user."))

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))
