# ShopEase — Full-Stack E-Commerce Platform

A complete, production-grade e-commerce web application engineered with **Django 3.2 LTS**, **SQLite**, and modern **HTML5/CSS3/Vanilla JS** for an internship project demonstration.

---

## 🌟 Core Features & Capabilities

### 1. Catalog & Product Discovery
* **Category Browsing**: 5 departments (Audio & Electronics, Wearables & Timepieces, Everyday Bags & Travel, Home & Workspace, Footwear & Apparel).
* **Detailed Product Pages**: High-resolution image showcases, stock indicators (In Stock, Low Stock count, Out of Stock), customer rating displays, discounted pricing badges, and SKU tags.
* **Instant Keyword Search**: Live filtering by product title and description.
* **Refined Filtering**: Real-time filtering by category, numeric price range (Min/Max), and in-stock availability.
* **Flexible Sorting**: Sort by Newest, Price (Low to High), Price (High to Low), Customer Rating, and Alphabetical.

### 2. Shopping Cart System
* **Session & User Hybrid Architecture**: Guest visitors can add items to their session-based cart. Upon registration or login, guest items are automatically migrated and merged into the user's permanent profile.
* **Real-time Quantity Controls**: Adjust quantities directly in the cart with instant subtotal and total recalculations.
* **Stock Boundary Protection**: Prevents users from requesting more items than are available in current inventory.
* **Free Shipping Incentive**: Dynamic progress banner showing remaining amount to reach free shipping ($75 threshold).

### 3. Secure Checkout & Order Processing
* **Atomic Transactions**: Uses Django's `transaction.atomic()` with database row locks (`select_for_update`) to prevent inventory overselling or concurrent checkouts.
* **Price Snapshotting**: Unit prices are permanently captured in `OrderItem` records at checkout time, insulating historical order summaries from future product price changes.
* **Payment Support**: Cash on Delivery (COD) workflow with verified billing/shipping addresses.
* **Immediate Inventory Deduction**: Decrements stock accurately upon placement and restores stock if an order is cancelled.

### 4. Authentication & User Profile
* **Secure Registration & Login**: Validated passwords, unique username/email checks, and session authentication.
* **Customer Profile Management**: Update personal names, email, and saved default delivery address (phone, street address, city, postal code).
* **Order History & Receipt Printing**: Complete order tracking timeline (Pending, Confirmed, Processing, Shipped, Delivered, Cancelled) and print-friendly receipts.

---

## 🔑 Demo Accounts for Evaluation

| Role | Username | Password | Notes |
| :--- | :--- | :--- | :--- |
| **Demo Customer** | `intern_demo` | `password123` | Pre-loaded with order history and profile details |
| **Store Superuser** | `admin` | `admin123` | Full access to Django Administration panel (`/admin/`) |

*Tip: The Sign In page features a 1-click **"Autofill Demo Credentials"** button for quick evaluator testing.*

---

## 🏗️ Architecture & Database Models

```
Category (id, name, slug, description, image)
   └── Product (id, category_id, name, slug, description, price, discount_price, stock_quantity, rating, review_count, is_featured, is_active)
          ├── CartItem (cart_id, product_id, quantity)
          └── OrderItem (order_id, product_id, product_name, price, quantity, subtotal)

User
   ├── UserProfile (phone, address, city, postal_code)
   ├── Cart (session_key, user_id)
   └── Order (order_number, user_id, status, subtotal, shipping_cost, total, shipping fields)
```

---

## 🧪 Automated Test Suite

ShopEase includes 24 comprehensive unit and integration tests covering the complete user lifecycle:

```bash
python manage.py test
```

### Coverage:
* Complete end-to-end user journey from search, add-to-cart, registration, checkout, order details, logout, and re-login.
* User registration, password matching validation, and unique constraint enforcement.
* Authentication and session management.
* Product catalog listing, category filtering, search queries, and 404 handlers.
* Cart operations: item addition, increment, decrement, stock limits, and removal.
* Checkout atomicity, inventory deduction, order snapshot accuracy, and cross-user authorization security.
* Order cancellation and stock restoration.

---

## 💻 Tech Stack Summary

* **Backend Framework**: Django 3.2 LTS (Python 3.11)
* **Database**: SQLite3 (with PostgreSQL migration support via dj-database-url)
* **Frontend**: Django Templates, Semantic HTML5, Responsive CSS3 Grid/Flexbox, Vanilla ES6 JavaScript
* **Icons & Imagery**: Vector SVGs and Lucide icons
