from django.db import models
import uuid
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from datetime import timedelta

from .managers import MyAccountManager 

class CustomUser(AbstractBaseUser, PermissionsMixin):

    first_name = models.CharField(max_length = 50)
    last_name = models.CharField(max_length = 50)
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(verbose_name= "Enter your email", unique=True)
    phone_number = PhoneNumberField(null=True, blank=True, unique=True, region = "NP")
    date_of_birth = models.DateField(null=True, blank=True)

    date_joined = models.DateTimeField(default=timezone.now)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = MyAccountManager()

    def __str__(self):
        return self.email


class EmailVerificationToken(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        expiry_time = self.created_at + timedelta(hours=24)
        return timezone.now() > expiry_time
    
    def  __str__(self):
        return f"Verification token for {self.user.email}"