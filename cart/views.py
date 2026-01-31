from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Cart, CartItem
from .serializers import (
    CartSerializer,
    CartItemSerializer,
    AddToCartSerializer,
    UpdateCartItemSerializer,
)

# Create your views here.

class CartViewSet(viewsets.GenericViewSet):
    """ViewSet for managing the shopping cart"""
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_or_create_cart(self):
        """Get or create the cart for the authenticated user"""
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart
    
    def list(self, request):
        """Retrieve the current user's cart"""
        cart = self.get_or_create_cart()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path='add')
    def add_item(self, request):
        """Add an item to the cart"""
        cart = self.get_or_create_cart()
        serializer = AddToCartSerializer(data=request.data)
        if serializer.is_valid():
            cart_item = serializer.save(cart=cart)
            response_data = {
                "message": "Item added to cart successfully.",
                "cart_item": CartItemSerializer(cart_item).data,
                "cart": CartSerializer(cart).data
            }

            if hasattr(cart_item, 'warning') and cart_item.warning:
                response_data['warning'] = cart_item.warning

            return Response(response_data, status = status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail = False, methods = ['put', 'patch'], url_path='items/(?P<item_id>[^/.]+)/update') 
    # url_path uses regex, so we use (?P<item_id>[^/.]+) to capture item_id

    def update_item(self, request, item_id=None):
        """Update the quantity of a cart item"""
        cart = get_object_or_404(Cart, user=self.request.user)
        
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        serializer = UpdateCartItemSerializer(data=request.data, context = {'cart_item': cart_item})
        if serializer.is_valid():
            serializer.update(cart_item, serializer.validated_data)
            return Response({
                "message": "Cart item updated successfully.",
                "cart_item": CartItemSerializer(cart_item).data,
                "cart": CartSerializer(cart).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail = False, methods = ['delete'], url_path='items/(?P<item_id>[^/.]+)/remove')
    def remove_item(self, request, item_id=None):
        """Remove item from the cart"""
        cart = get_object_or_404(Cart, user=self.request.user)

        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        product_name = cart_item.product.name
        cart_item.delete()
        return Response({
            "message": f"'{product_name}' removed from cart",
            "cart": CartSerializer(cart).data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['delete'], url_path='clear')
    def clear_cart(self, request):
        """Clear all items from the cart"""
        cart = get_object_or_404(Cart, user=self.request.user)
        if cart.is_empty():
            return Response({
                'message': 'Cart is already empty',
                'cart': CartSerializer(cart).data
            }, status=status.HTTP_200_OK)
        
        cart.clear()
        return Response({
            'message': 'Cart cleared successfully',
            'cart': CartSerializer(cart).data
        }, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['get'], url_path='count')
    def item_count(self, request):
        """Get the total number of items in the cart"""
        cart = self.get_or_create_cart()
        return Response({
            'total_items': cart.total_items,
            'total_unique_items': cart.total_unique_items
        }, status=status.HTTP_200_OK)