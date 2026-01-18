from django.urls import path
from . import views



urlpatterns = [
    path("register/", views.UserRegistrationAPIView.as_view(), name="user_register"),
    path("verify-email/", views.VerifyEmailAPIView.as_view(), name="verify_email"),
    path("resend-verification/", views.ResendVerificationEmailAPIView.as_view(), name="resend_verification"),
    path("me/", views.UserProfileAPIView.as_view(), name="user_profile"),
    path("logout/", views.LogoutView.as_view(), name= "user_logout"),
    path("google/callback/", views.GoogleOAuthCallbackAPIView.as_view(), name="google_oauth_callback"),
   
]

