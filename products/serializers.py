from rest_framework import serializers
from .models import Product, Category, ProductImage, ProductReview
from django.contrib.auth import get_user_model
from django.db.models import Avg


User = get_user_model()



class CategorySerializer(serializers.ModelSerializer):
    """Serializer for category list and detail view"""

    subcategories = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()
    full_path = serializers.CharField(source='get_full_path', read_only=True)
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'parent', 'image', 'is_active', 'full_path',
            'subcategories', 'product_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']
    
    def get_subcategories(self, obj):
        """
        Get immediate child categories
        """
        subcategories = obj.subcategories.filter(is_active=True)
        return CategorySerializer(subcategories, many=True, context=self.context).data # recursive serialization / .data converts the modeel instance into python primitives/JSON-ready
    
    def get_product_count(self, obj):
        """
        Count active products in this category
        """
        count = obj.products.filter(is_active=True).count()
        return count


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for product images"""
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'order']
        read_only_fields = ['id']




class ProductReviewSerializer(serializers.ModelSerializer):
    """Serializer for product reviews"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = ProductReview
        fields = [
            'id', 'product', 'user', 'user_name', 'user_email',
            'rating', 'title', 'comment', 'is_verified_purchase',
            'is_approved', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'is_verified_purchase', 'created_at', 'updated_at', 'user_name', 'user_email']
        
    def validate_rating(self, value):
        """
        Validate rating is between 1 and 5

        """
      
        def validate_rating(self, value):
            if not 1 <= value <= 5:
                raise serializers.ValidationError("Rating must be between 1 and 5")
            return value
    
    def create(self, validated_data):
        """
        Auto-assign current user when creating review
        """
      
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)



class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for product listings"""
    

    category_name = serializers.CharField(source='category.name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'short_description', 
            'category', 'category_name', 'price', 'compare_at_price',
            'discount_percentage', 'primary_image', 'is_in_stock',
            'is_featured', 'average_rating', 'review_count', 'brand'
        ]
    
    def get_primary_image(self, obj):
        """
        Get the primary product image URL
        """
        primary = obj.images.filter(is_primary=True).first()
        if primary:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(primary.image.url)
            return None
    
    def get_average_rating(self, obj):
        """
        Calculate average rating from approved reviews
        
        """
        reviews = obj.reviews.filter(is_approved=True)
        if reviews.exists():
            average = reviews.aggregate(Avg('rating'))['rating__avg']
            return round(average, 1)
        return 0
    
    def get_review_count(self, obj):
        """
        Count approved reviews
        """
        return obj.reviews.filter(is_approved=True).count()




class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single product view"""
    


    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )
    images = ProductImageSerializer(many=True, read_only=True)
    reviews = ProductReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'short_description',
            'category', 'category_id', 'price', 'compare_at_price',
            'discount_percentage', 'sku', 'stock_quantity',
            'low_stock_threshold', 'brand', 'weight',
            'is_active', 'is_featured', 'is_in_stock', 'is_low_stock',
            'images', 'reviews', 'average_rating', 'review_count',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'slug', 'sku', 'discount_percentage',
            'is_in_stock', 'is_low_stock', 'created_by',
            'created_at', 'updated_at'
        ]
    
    def get_average_rating(self, obj):
        """Calculate average rating"""
        reviews = obj.reviews.filter(is_approved=True)
        if reviews.exists():
            average = reviews.aggregate(Avg('rating'))['rating__avg']
            return round(average, 1)
        return 0
    
    def get_review_count(self, obj):
        """Count reviews"""
        return obj.reviews.filter(is_approved=True).count()
    
    def create(self, validated_data):
        """
        Auto-assign creator when creating product
        """
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
        




class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating products"""
    
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'short_description', 'category',
            'price', 'compare_at_price', 'stock_quantity',
            'low_stock_threshold', 'brand', 'weight',
            'is_active', 'is_featured'
        ]
    
    def validate(self, data):
        """
        Cross-field validation
        
        """
        if data.get('compare_at_price') and data.get('price'):
            if data['compare_at_price'] < data['price']:
                raise serializers.ValidationError({
                    'compare_at_price': 'Must be greater than or equal to price'
                })
        return data
        
    
    def create(self, validated_data):
        """Auto-assign creator"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)