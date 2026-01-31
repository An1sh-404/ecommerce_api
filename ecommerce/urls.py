"""
URL configuration for ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView
from accounts.views import CustomTokenObtainPairView
from dj_rest_auth.views import (
    PasswordResetView,
    PasswordResetConfirmView,
    PasswordChangeView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include('accounts.urls')),
    path("api/auth/login/", CustomTokenObtainPairView.as_view(), name= "token_obtain"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/password/reset/", PasswordResetView.as_view(), name="password_reset"),
    path("api/auth/password/reset/confirm/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("api/auth/password/change/", PasswordChangeView.as_view(), name="password_change"),
    path("accounts/", include("allauth.urls")),
    
    # Products API
    path("api/", include('products.urls')),
    path("api/cart/", include('cart.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
