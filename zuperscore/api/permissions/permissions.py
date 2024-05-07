from rest_framework.permissions import BasePermission


class IsUserManager(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == "user_manager")


class IsPlatformAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == "admin")

class IsNotStudent(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.role != "student")

class IsAdminOrUserManager(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.role in ['admin', 'user_manager'])