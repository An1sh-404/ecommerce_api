from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

class EmailOrUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            user = User.objects.get(
                Q(username__iexact = username) | Q(email__iexact = username)
            )

        except User.DoesNotExist:
            User().set_password(password)
            return None
        
        except User.MultipleObjectsReturned:
            logger.error(f"Multiple users found with username or email: {username}")
            return None
        
        if user.check_password(password) and self.user_can_authenticate(user):
            logger.info(f"User {username} authenticated successfully.")
            return user
        
        return None
    
    def get_user(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
            return user if self.user_can_authenticate(user) else None # checks if user.is_active
        except User.DoesNotExist:
            return None