from rest_framework import serializers
from .models import Cart, CartItem
from products.models import Product
from products.serializers import ProductDetailSerializer
from django.db import transaction

class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for individual cart items"""

    product = ProductDetailSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )

    unit_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    is_available = serializers.BooleanField(read_only=True)
    is_quantity_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = CartItem
        fields = [
            'id','product', 'product_id', 'quantity',
            'unit_price', 'total_price', 'is_available', 'is_quantity_available',
            'added_at', 'updated_at'
        ]
        read_only_fields = ['id', 'added_at', 'updated_at']

    def validate(self, attrs):
        product = attrs.get('product')
        quantity = attrs.get('quantity', 1)

        if not product.is_active:
            raise serializers.ValidationError(f"Product '{product.name}' is not available.")
        
        if not product.is_in_stock:
            raise serializers.ValidationError(f"Product '{product.name}' is out of stock.")

        if quantity > product.stock_quantity:
            raise serializers.ValidationError(f"Only {product.stock_quantity} units of '{product.name}' available in store.")

        return attrs
    

class CartSerializer(serializers.ModelSerializer):
    """Serializer for the shopping cart"""
    
    items = CartItemSerializer(many=True, read_only=True) # Cart.items gives all cart items related to this cart.
    total_items = serializers.IntegerField(read_only=True)
    subtotal = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    total_unique_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 
                  'user', 
                  'items', 
                  'total_items', 
                  'subtotal', 
                  'total_unique_items', 
                  'created_at',
                  'updated_at'
                  ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class AddToCartSerializer(serializers.Serializer):
    """Serializer for adding items to the cart"""
    
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate_product_id(self, value):
        try:
            product = Product.objects.get(id=value, is_active=True)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found or not available.")
        
        return value
    
    def validate(self, attrs):
        product_id = attrs['product_id']
        quantity = attrs['quantity']

        try:
            product = Product.objects.get(id=product_id)
            if not product.is_in_stock:
                raise serializers.ValidationError({
                    'product_id': f"Product '{product.name}' is out of stock."
                })
            
            if quantity > product.stock_quantity:
                raise serializers.ValidationError({
                    'quantity':f"Only {product.stock_quantity} units of '{product.name}' available"
                })
        except Product.DoesNotExist:
            pass # Handled in validate_product_id

        return attrs
    
    @transaction.atomic
    def save(self, cart):
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']

        product = Product.objects.get(id=product_id)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        warning_message = None

        if not created:

            requested_quantity = cart_item.quantity + quantity
            available_to_add = product.stock_quantity - cart_item.quantity
            
            if requested_quantity > product.stock_quantity:
                if available_to_add > 0:
                    cart_item.quantity = product.stock_quantity
                    warning_message = (
                    f"Only {available_to_add} more unit{'s' if available_to_add != 1 else ''} available. "
                    f"Cart updated to maximum ({product.stock_quantity} total)."
                    )

                else:

                    warning_message = (
                    f"Cart already contains maximum available quantity ({product.stock_quantity} units). "
                    f"No items added."
                    )
            
            else:
                cart_item.quantity = requested_quantity
            
            cart_item.save()

        
        cart_item.warning = warning_message
        return cart_item    
    

class UpdateCartItemSerializer(serializers.Serializer):
    """Serializer for updating cart item quantity"""
    quantity = serializers.IntegerField(min_value=1)
    def validate(self, attrs):
        cart_item = self.context.get('cart_item')
        quantity = attrs['quantity']

        if cart_item and quantity > cart_item.product.stock_quantity:
            raise serializers.ValidationError({
                'quantity': f"Only {cart_item.product.stock_quantity} units available"
            })
        return attrs
    
    def update(self, instance, validated_data):
        instance.quantity = validated_data['quantity']
        instance.save()
        return instance