# Rest framework
from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Object level permission. Check if the requesting user is the author or not. If he/she the author then we will give him/her a read and write permission otherwise ready only
    """
    def has_object_permission(self, request, view, obj):
        # Check if he requesting for only a get, etc
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.author == request.user
