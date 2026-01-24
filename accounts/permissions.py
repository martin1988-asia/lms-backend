from rest_framework import permissions


class RolePermission(permissions.BasePermission):
    """
    Unified role-based permission.

    Usage examples:
        # Pass the class (DRF will instantiate with no args)
        permission_classes = [permissions.IsAuthenticated, RolePermission]

        # Or use a subclass with roles configured
        permission_classes = [
            permissions.IsAuthenticated,
            IsStudent
        ]
    """

    allowed_roles = []
    allow_read_only = False

    def has_permission(self, request, view):
        # Always allow safe methods if allow_read_only is True
        if self.allow_read_only and request.method in permissions.SAFE_METHODS:
            return True

        if not request.user or not request.user.is_authenticated:
            return False

        # Admin override: staff/superuser always allowed
        if request.user.is_staff or request.user.is_superuser:
            return True

        # ✅ Check role field directly
        if hasattr(request.user, "role") and request.user.role in self.allowed_roles:
            return True

        return False

    def __str__(self):
        return f"RolePermission(roles={self.allowed_roles}, read_only={self.allow_read_only})"


# ✅ Backwards-compatible individual permissions using class attributes
class IsInstructor(RolePermission):
    allowed_roles = ["instructor"]


class IsStudent(RolePermission):
    allowed_roles = ["student"]


class IsAdmin(RolePermission):
    allowed_roles = ["admin"]


class ReadOnly(RolePermission):
    allow_read_only = True
