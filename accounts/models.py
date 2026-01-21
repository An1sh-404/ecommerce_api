from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone

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