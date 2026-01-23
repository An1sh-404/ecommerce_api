from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q, Avg
from django_filters.rest_framework import DjangoFilterBackend

from .models import Category, Product, ProductImage, ProductReview
from .serializers import (
    CategorySerializer, ProductListSerializer, ProductDetailSerializer, ProductCreateUpdateSerializer, ProductImageSerializer, ProductReviewSerializer
)
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin

# Create your views here.

class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing categories"""
    
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def products(self, request, slug=None):
        """Get all products in this category"""
        category = self.get_object()
        products = Product.objects.filter(category=category, is_active=True)
        serializer = ProductListSerializer(products, many=True, context={'request':request})
        return Response(serializer.data)
    

class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for managing products"""
    
    queryset = Product.objects.filter(is_active=True)
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__slug', 'brand', 'price']
    search_fields = ['name', 'description', 'short_description', 'sku', 'brand']
    ordering_fields = ['price', 'name', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        elif self.action == 'retrieve':
            return ProductDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductDetailSerializer
    
    def get_queryset(self):
        queryset =  super().get_queryset()

        queryset = queryset.select_related('category', 'created_by')
        queryset = queryset.prefetch_related('images', 'reviews')

        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')

        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        in_stock = self.request.query_params.get('in_stock')
        if in_stock and in_stock.lower() == 'true':
            queryset = queryset.filter(stock_quantity__gt=0)

        min_rating = self.request.query_params.get('min_rating')
        if min_rating:
            queryset = queryset.annotate(
                avg_rating=Avg('reviews__rating')
            ).filter(avg_rating__gte=min_rating)
        
        return queryset
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def upload_image(self, request, slug=None):
        """Upload an image for the product"""
        product = self.get_object()
        serializer = ProductImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, slug=None):
        """Get all reviews for this product"""
        product= self.get_object()
        reviews = product.reviews.filter(is_approved=True)
        serializer = ProductReviewSerializer(
            reviews,
            many=True,
            context={'request':request}
        )
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured products. Returns upto 10 featured products."""
        featured_products = self.get_queryset().filter(is_featured=True)
        serializer = ProductListSerializer(
            featured_products,
            many=True,
            context={'request':request}
        )
        return Response(serializer.data)