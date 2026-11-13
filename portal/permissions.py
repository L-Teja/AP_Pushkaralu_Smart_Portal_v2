from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and (
            request.user.is_superuser or
            (hasattr(request.user, "profile") and request.user.profile.role == "admin")
        ))

class IsPoliceOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return hasattr(request.user, "profile") and request.user.profile.role in ("police", "admin")
