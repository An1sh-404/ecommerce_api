from django.contrib import admin
from .models import Category, Product, ProductImage, ProductReview
# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_active', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    list_filter = ('is_active', 'parent')


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]  # Edit images within product form
    list_display = ('name', 'category', 'price', 'stock_quantity', 'is_active', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description', 'sku', 'brand')
    list_filter = ('is_active', 'category', 'brand')
    ordering = ('-created_at',)


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'title', 'rating', 'is_approved', 'is_verified_purchase', 'created_at')
    search_fields = ('product__name', 'user__username', 'user__email', 'comment', 'title')
    list_filter = ('is_approved', 'is_verified_purchase', 'rating', 'created_at')
    ordering = ('-created_at',)
    readonly_fields = ('user', 'product', 'created_at', 'updated_at')
    actions = ['approve_reviews', 'reject_reviews']

    def approve_reviews(self, request, queryset):
        """Admin action to approve selected reviews"""
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} review(s) approved.")

    def reject_reviews(self, request, queryset):
        """Admin action to reject selected reviews"""
        updated = queryset.update(is_approved=False)
        self.message_user(request, f"{updated} review(s) rejected.")