"""
URL configuration for products app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router and register viewsets
router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'images', views.ProductImageViewSet, basename='productimage')
router.register(r'reviews', views.ProductReviewViewSet, basename='productreview')

urlpatterns = [
    path('', include(router.urls)),
]

"""
Generated URLs:

Categories:
- GET    /api/categories/                    - List all categories
- POST   /api/categories/                    - Create category (admin)
- GET    /api/categories/{slug}/             - Get category details
- PUT    /api/categories/{slug}/             - Update category (admin)
- PATCH  /api/categories/{slug}/             - Partial update (admin)
- DELETE /api/categories/{slug}/             - Delete category (admin)
- GET    /api/categories/{slug}/products/    - Get products in category

Products:
- GET    /api/products/                      - List all products
- POST   /api/products/                      - Create product (admin)
- GET    /api/products/{slug}/               - Get product details
- PUT    /api/products/{slug}/               - Update product (admin)
- PATCH  /api/products/{slug}/               - Partial update (admin)
- DELETE /api/products/{slug}/               - Delete product (admin)
- POST   /api/products/{slug}/upload_image/  - Upload product image
- GET    /api/products/{slug}/reviews/       - Get product reviews
- GET    /api/products/featured/             - Get featured products
- GET    /api/products/low_stock/            - Get low stock products (admin)

Product Images:
- GET    /api/images/                        - List all images
- POST   /api/images/                        - Upload image (admin)
- GET    /api/images/{id}/                   - Get image details
- PUT    /api/images/{id}/                   - Update image (admin)
- PATCH  /api/images/{id}/                   - Partial update (admin)
- DELETE /api/images/{id}/                   - Delete image (admin)

Product Reviews:
- GET    /api/reviews/                       - List all reviews
- POST   /api/reviews/                       - Create review (authenticated)
- GET    /api/reviews/{id}/                  - Get review details
- PUT    /api/reviews/{id}/                  - Update review (owner/admin)
- PATCH  /api/reviews/{id}/                  - Partial update (owner/admin)
- DELETE /api/reviews/{id}/                  - Delete review (owner/admin)
- POST   /api/reviews/{id}/approve/          - Approve review (admin)

Query Parameters:
Products:
  - ?min_price=100&max_price=500            - Price range filter
  - ?in_stock=true                          - Only in-stock products
  - ?min_rating=4                           - Minimum rating filter
  - ?category__slug=electronics             - Filter by category
  - ?brand=Apple                            - Filter by brand
  - ?search=laptop                          - Search by keyword
  - ?ordering=price                         - Sort by price (ascending)
  - ?ordering=-price                        - Sort by price (descending)

Reviews:
  - ?product=123                            - Filter by product ID
  - ?rating=5                               - Filter by rating
  - ?ordering=-created_at                   - Sort by newest first
"""
