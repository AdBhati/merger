from rest_framework.permissions import BasePermission, SAFE_METHODS


# Auth permissions
class IsUserManager(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == "user_manager")


class IsPlatformAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == "admin")


class IsNotStudentOrGuest(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.role not in ["user", "guest"])


class IsAdminOrUserManager(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.role in ["admin", "user_manager"])


class IsManager(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.role in ["manager", "sso_manager", "prep_manager"]
        )


class IsOpsMananger(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == "manager")


class IsSsoManager(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == "sso_manager")


class IsPrepMananger(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == "prep_manager")


class IsTutor(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == "tutor")


class IsParent(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == "parent")


class IsCounselor(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == "counselor")


class IsTypist(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == "typist")


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == "user")


class IsGuest(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == "guest")


# read only permissions





# class IsManagerReadOnly(IsManager):
#     def has_object_permission(self, request, view, obj):
#         # Read-only permission for students
#         return request.method in SAFE_METHODS


def read_only(permission_class):
    """
    Factory function to create a read-only permission class based on another permission class.
    """

    class IsReadOnly(permission_class):
        def has_object_permission(self, request, view, obj):
            # Read-only permission for all requests
            return request.method in SAFE_METHODS

    return IsReadOnly


class ReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read-only permission for all requests
        return request.method in SAFE_METHODS
