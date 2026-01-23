from django.shortcuts import render
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, UserRegistrationSerializer, CustomTokenObtainPairSerializer
from .tokens import EmailVerificationToken
from .utils import send_verification_email


# Create your views here.
User = get_user_model()


class UserRegistrationAPIView(generics.CreateAPIView):
    #queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # Generate email verification token
        verification_token = EmailVerificationToken.create_token(user=user)
        # Send verification email
        send_verification_email(user, verification_token)
        return Response(
            {
                "message":"Registration successfull! Please check your email to verify your account before logging in.",
                "email":user.email,
                "detail":"A verification link has been sent to your email address."

            }, status = status.HTTP_201_CREATED)
        

        # Generates JWT tokens for the registered users.
        # refresh = RefreshToken.for_user(user)

        # return Response({
        #     "user": UserSerializer(user).data,
        #     "tokens": {
        #         "refresh": str(refresh),
        #         "access":str(refresh.access_token),
        #     },
        #     "message":"User registered successfully!"
        # }, status = status.HTTP_201_CREATED
        # )


class VerifyEmailAPIView(APIView):
    """
    Verify user's email using the JWT token from email link
    """
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Handle GET request with token parameter
        """
        token = request.query_params.get("token")
        if not token:
            return Response(
                {
                    "error":"No verification token provided.",
                    "detail":"Please provide a valid verification token."
                },
                status = status.HTTP_400_BAD_REQUEST
            )
        
        user = EmailVerificationToken.verify_token(token)
        if user is None:
            return Response(
                {
                    "error":"Invalid or expired verification token.",
                    "detail":"Please request a new verification email."
                },
                status = status.HTTP_400_BAD_REQUEST
            )
        
        if user.is_active:
            # User already verified
            return Response(
                {
                    "message":"Email already verified. You can log in.",
                },
                status = status.HTTP_200_OK
            )
        
        # Activate user
        user.is_active = True
        user.email_verified = True
        user.save()

        # Now give them auth tokens so they can login immediately
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message":"Email verified successfully! You can now log in.",
                "user" : UserSerializer(user).data,
                "tokens":{
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                }
            },
            status = status.HTTP_200_OK
        )


class ResendVerificationEmailAPIView(APIView):
    """
    Resend verification email to unverified users
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response(
                {
                    "error":"Email is required to resend verification email.",
                    "detail":"Please provide your email address."
                },
                status = status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
            if user.is_active:
                return Response(
                    {
                        "message":"If an account with this email exists and is not verified, a new verification email has been sent.",
                        "detail":"Please check your email inbox and spam folder."
                    },
                    status = status.HTTP_200_OK
                )
            
            # Generate new verification token
            verification_token = EmailVerificationToken.create_token(user=user)
            send_verification_email(user, verification_token)

            return Response(
                {
                    "message":"If an account with this email exists and is not verified, a new verification email has been sent.",
                    "detail":"Please check your email inbox and spam folder."
                },
                status = status.HTTP_200_OK
            )

        except User.DoesNotExist:
            # Always return the same response to avoid user enumeration
            return Response(
                {
                    "message":"If an account with this email exists and is not verified, a new verification email has been sent.",
                    "detail":"Please check your email inbox and spam folder."
                },
                status = status.HTTP_200_OK
            )


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer



class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"error": "No Refresh token provided."}, status=status.HTTP_400_BAD_REQUEST
                )
            
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"message" : "Successfully logged out"},
                status = status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status = status.HTTP_400_BAD_REQUEST
            )






class UserProfileAPIView(generics.RetrieveUpdateAPIView):

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


    

class GoogleOAuthCallbackAPIView(APIView):
    """Custom oauth callback that return JWT tokens."""

    permission_classes = [AllowAny]

    def get(self, request):
        """Handle GET request after successful Google OAuth login."""
        user = request.user
        if not user.is_authenticated:
            return Response(
                {
                    "error": "oauth_failed.",
                    "message": "Google authentication failed."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Generate JWT tokens for the authenticated user
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Google OAuth login successful.",
                "user": UserSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
            },
            status=status.HTTP_200_OK
        )