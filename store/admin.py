from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Order, OrderItem, UserProfile


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'product_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'price',
        'discount_price',
        'stock_quantity',
        'available',
        'is_featured',
        'rating',
        'created_at',
    )
    list_filter = ('category', 'available', 'is_featured', 'created_at')
    list_editable = ('price', 'discount_price', 'stock_quantity', 'available', 'is_featured')
    search_fields = ('name', 'description', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'price', 'quantity', 'subtotal')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number',
        'full_name',
        'email',
        'total',
        'payment_method',
        'order_status',
        'created_at',
    )
    list_filter = ('order_status', 'payment_method', 'created_at')
    list_editable = ('order_status',)
    search_fields = ('order_number', 'full_name', 'email', 'phone', 'address')
    readonly_fields = (
        'order_number',
        'user',
        'subtotal',
        'shipping_cost',
        'total',
        'payment_method',
        'created_at',
        'updated_at',
    )
    inlines = [OrderItemInline]
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'get_subtotal')

    def get_subtotal(self, obj):
        return f"${obj.get_subtotal():.2f}"
    get_subtotal.short_description = 'Subtotal'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_key', 'total_items', 'total_price', 'updated_at')
    inlines = [CartItemInline]
    readonly_fields = ('created_at', 'updated_at')

    def total_items(self, obj):
        return obj.get_total_items()
    total_items.short_description = 'Items'

    def total_price(self, obj):
        return f"${obj.get_total():.2f}"
    total_price.short_description = 'Total'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'city', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone', 'city')
