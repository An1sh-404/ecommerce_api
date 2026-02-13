from django.db import transaction
from django.db.models import Q
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'first_name', 'last_name', 'username', 'email',
            'phone_number', 'date_of_birth', 'date_joined',
            'is_active'
        ]
        read_only_fields = ['date_joined', 'is_active']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text='Confirm your password.'
        )
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 
            'phone_number', 'date_of_birth','username', 'email', 'password', 'password_confirm'
        ]
        extra_kwargs = {
            'password': {'write_only':True,
                         'style':{'input_type':'password'}},
            'email':{'required':True},
            'username':{'required':True},
        }

    
    def validate_password(self, value):
        try:
            validate_password(value) # django's built-in password validator
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        return data
    

    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        with transaction.atomic():
            user = User.objects.create_user(**validated_data)
        
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'username' # Tells parent to look for 'username' in JSON

    def validate(self, attrs):
        username_value = attrs.get(self.username_field)
        password = attrs.get('password')

        try:
            user = User.objects.get(
                Q(username__iexact=username_value) | Q(email__iexact=username_value)
            )
            if user.check_password(password):
                if not user.is_active:
                    raise serializers.ValidationError({
                        "error": "email_not_verified",
                        "error_description": "Email verification is required before logging in.",
                        "message": "Please verify your email before logging in.",
                        "email": user.email,
                        "actions": {
                            "resend_verification" : "/api/accounts/resend-verification/"
                        }
                    })
        except User.DoesNotExist:
            pass  # Let the parent class handle authentication failure
        except User.MultipleObjectsReturned:
            pass

        return super().validate(attrs)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field] = serializers.CharField()
        self.fields[self.username_field].label = "Email or Username"

    
