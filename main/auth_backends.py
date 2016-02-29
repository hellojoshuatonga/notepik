# Custom
from .models import NotepikUser

class NotepikUserAuthBackend(object):
    """
    Authentication backend for our NotepikUser.
    """
    def authenticate(self, key):
        return NotepikUser.objects.get_or_none(key=key)

    def get_user(self, user_id):
        return NotepikUser.objects.get_or_none(pk=user_id)
