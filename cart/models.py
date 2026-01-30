from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

from products.models import Product

from decimal import Decimal

# Create your models here.

User = get_user_model()

class Cart(models.Model):
    user = models.OneToOneField(User,related_name='cart', on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True,db_index=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"
        ordering = ['-updated_at']

    def __str__(self):
        if self.user:
            return f"User Cart: {self.user.email}"
        return f"Session Cart: {self.session_key[:8]}..."

    def clean(self):
        if not self.user and not self.session_key:
            raise ValidationError("Cart must have either user or session_key")
        
    def save(self, *args, **kwargs):
        self.full_clean() # Call clean method before saving, clean only runs custom validations while full_clean runs all validations
        super().save(*args, **kwargs)

    
    @property
    def total_items(self):
        """Total number of items in the cart"""
        return sum(item.quantity for item in self.items.all())
    
    @property
    def subtotal(self):
        """Calculate subtotal cost of items in the cart"""
        total = Decimal('0.00')
        for item in self.items.all():
            total += item.product.price * item.quantity
        return total
    
    @property
    def total_unique_items(self):
        """Count of different products in the cart"""
        return self.items.count()
    
    def is_empty(self):
        """Check if cart is empty"""
        return self.items.count() == 0
    
    def clear(self):
        """Empty the cart by deleting all items"""
        self.items.all().delete()



class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('cart', 'product')  # Prevent duplicates
        ordering = ['-added_at']  # Newest items first
        indexes = [
            models.Index(fields=['cart', 'product']),  # Fast lookups, allows same cart with differnet cartitems,  and different products. Like for same product cart items with differnent cart.
        ]
        # One cart have multiple cart items with different products.
        # for eg; cart A -> CartItem(cart=A, product=Book, quantity=2), CartItem(cart=A, product=Laptop), CartItem(cart=A, product=iphone) and so on.
        # Same product appear in muliptle carts but only once per cart ,rest use quantity to manage multiples.
        # for eg; CartItem(cart=A, product=Book, quantity=2) and CartItem(cart=B, product=Book, quantity=1)
        # cartitems with same cart A and product laptop or books or any are not allowed.

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in cart"
    




    def clean(self):
        if not self.product.is_active:
            raise ValidationError(f"Product '{self.product.name}' is not available.")
        
        if self.quantity > self.product.stock_quantity:
            raise ValidationError(f"Only {self.product.stock_quantity} units of '{self.product.name}' available in store.")    
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def unit_price(self):
        """Get current unit price of the product"""
        return self.product.price
    
    @property
    def total_price(self):
        """Calculate total price for this cart item"""
        return Decimal(self.quantity) * self.unit_price
    
    @property
    def is_available(self):
        """Check if product is still in stock and active"""
        return self.product.is_active and self.product.is_in_stock
    
    @property
    def is_quantity_available(self):
        """Check if requested quantity is in stock"""
        return self.quantity <= self.product.stock_quantity