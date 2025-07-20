from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend

class EmailAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=username)  # Look up user by email
            if user.check_password(password):  # Check if the password matches
                return user
        except User.DoesNotExist:
            return None
