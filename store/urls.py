from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('products/', views.product_list_view, name='products'),
    path('category/<slug:category_slug>/', views.product_list_view, name='products_by_category'),
    path('products/category/<slug:category_slug>/', views.product_list_view, name='products_by_category_alt'),
    path('product/<slug:slug>/', views.product_detail_view, name='product_detail'),

    # Cart endpoints
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart_view, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_view, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart_view, name='remove_from_cart'),
    path('cart/clear/', views.clear_cart_view, name='clear_cart'),

    # Checkout & Orders
    path('checkout/', views.checkout_view, name='checkout'),
    path('orders/', views.orders_view, name='orders'),
    path('orders/<str:order_number>/', views.order_detail_view, name='order_detail'),
    path('orders/<str:order_number>/cancel/', views.cancel_order_view, name='cancel_order'),

    # Authentication & Profile
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),

    # Information pages
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
]
