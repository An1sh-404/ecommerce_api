from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom adapter to handle social account actions.
       Called when a user is about to be logged in via OAuth.
    """

    def pre_social_login(self, request, sociallogin):

        """Link social account to existing user if email matches."""

        # If user is already logged in, do nothing

        if sociallogin.is_existing:
            return
        
        try:
            email = sociallogin.account.extra_data.get('email')
            if not email:
                return 
            

            user = User.objects.get(email__iexact=email)
            sociallogin.connect(request, user)

            if not user.is_active or not user.email_verified:
                user.is_active = True
                user.email_verified = True
                user.save()

        except User.DoesNotExist:
            pass

    
    def save_user(self, request, sociallogin, form=None):
        """Called when creating a new user via oauth"""
        user = super().save_user(request, sociallogin, form)
        
        if not user.username:
            user.username = user.email.split('@')[0]
        
        if not user.phone_number:
            user.phone_number = None
        
        if not user.date_of_birth:
            user.date_of_birth = None


        user.is_active = True
        user.email_verified = True
        user.save()
        
        return user



    