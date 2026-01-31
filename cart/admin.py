from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    """
    Inline display for cart items within cart admin.
    Shows all items in a table inside the cart detail page.
    """
    model = CartItem
    extra = 0  # Don't show empty forms for adding items
    readonly_fields = ['unit_price', 'total_price', 'added_at', 'updated_at']
    fields = ['product', 'quantity', 'unit_price', 'total_price', 'added_at']
    
    # Display methods for better formatting
    def unit_price(self, obj):
        """Display unit price with currency"""
        if obj.id:  # Only for saved items
            return f"${obj.unit_price}"
        return "-"
    unit_price.short_description = "Unit Price"
    
    def total_price(self, obj):
        """Display total price with currency"""
        if obj.id:  # Only for saved items
            return f"${obj.total_price}"
        return "-"
    total_price.short_description = "Total"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """
    Admin interface for Cart model.
    Provides overview of all carts with computed totals.
    """
    
    # List view configuration
    list_display = [
        'id',
        'user_email',
        'total_unique_items',
        'total_items',
        'subtotal_display',
        'created_at',
        'updated_at'
    ]
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__email', 'user__username', 'session_key']
    readonly_fields = [
        'created_at',
        'updated_at',
        'total_items',
        'subtotal',
        'total_unique_items'
    ]
    
    # Show cart items inline
    inlines = [CartItemInline]
    
    # Detail view organization
    fieldsets = (
        ('Cart Information', {
            'fields': ('user', 'session_key')
        }),
        ('Cart Summary', {
            'fields': ('total_unique_items', 'total_items', 'subtotal')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Collapsible section
        }),
    )
    
    # Custom display methods
    def user_email(self, obj):
        """Display user email or 'Anonymous' for guest carts"""
        if obj.user:
            return obj.user.email
        return f"Anonymous ({obj.session_key[:8]}...)"
    user_email.short_description = "User"
    user_email.admin_order_field = 'user__email'  # Allow sorting
    
    def subtotal_display(self, obj):
        """Display formatted subtotal"""
        return f"${obj.subtotal}"
    subtotal_display.short_description = "Subtotal"
    
    def has_add_permission(self, request):
        """
        Prevent manual cart creation through admin.
        Carts should only be created via API.
        """
        return False


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """
    Admin interface for CartItem model.
    Shows individual cart items across all carts.
    """
    
    list_display = [
        'id',
        'cart_user',
        'product',
        'quantity',
        'unit_price_display',
        'total_price_display',
        'is_available',
        'added_at'
    ]
    list_filter = ['added_at', 'updated_at', 'cart__user']
    search_fields = [
        'cart__user__email',
        'cart__user__username',
        'product__name',
        'product__sku'
    ]
    readonly_fields = [
        'unit_price',
        'total_price',
        'is_available',
        'is_quantity_available',
        'added_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Cart Item Information', {
            'fields': ('cart', 'product', 'quantity')
        }),
        ('Pricing', {
            'fields': ('unit_price', 'total_price')
        }),
        ('Availability', {
            'fields': ('is_available', 'is_quantity_available')
        }),
        ('Timestamps', {
            'fields': ('added_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Custom display methods
    def cart_user(self, obj):
        """Display which user owns this cart item"""
        if obj.cart.user:
            return obj.cart.user.email
        return f"Anonymous ({obj.cart.session_key[:8]}...)"
    cart_user.short_description = "Cart Owner"
    cart_user.admin_order_field = 'cart__user__email'
    
    def unit_price_display(self, obj):
        """Display formatted unit price"""
        return f"${obj.unit_price}"
    unit_price_display.short_description = "Unit Price"
    
    def total_price_display(self, obj):
        """Display formatted total price"""
        return f"${obj.total_price}"
    total_price_display.short_description = "Total Price"