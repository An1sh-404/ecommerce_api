from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import Token
import jwt

User = get_user_model()

class EmailVerificationToken:
    """
    JWT-based email verification token generator
    """

    @staticmethod
    def create_token(user):
        expiration = timedelta(hours=24)
        now = timezone.now()
        payload = {
            'user_id': user.id,
            'exp': int((now + expiration).timestamp()),
            'iat': int(now.timestamp()),
            'type': 'email_verification'
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm = 'HS256')
        return token


    @staticmethod
    def verify_token(token):
        try:
            decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            if decoded.get('type') != 'email_verification':
                return None
            
            user = User.objects.get(id=decoded['user_id'])
            return user
        
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except User.DoesNotExist:
            return None
    
        
