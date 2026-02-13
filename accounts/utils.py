from django.core.mail import send_mail
from django.conf import settings
import os

def send_verification_email(user,token):
    """
    Send verification email to user with JWT token
    """
    base_url = os.getenv("FRONTEND_URL", "http://localhost:8000")
    verification = f"{base_url}/api/auth/verify-email/?token={token}/"

    subject = "[Micro Ecommerce] Verify your email address"
    message = f"Hi {user.username}, Please verify your email by clicking the link below:\n{verification}\n\nThis link expires in 24 hours.\n\nIf you didn't create an account, please ignore this email.\n\n\nHappy Shopping!\nTheMicro Ecommerce Team"

    send_mail(
        subject, 
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )