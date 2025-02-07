from rest_framework.permissions import BasePermission
from user.models import UserRole

class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == UserRole.ADMIN
