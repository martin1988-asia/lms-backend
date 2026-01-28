from rest_framework import permissions


class RolePermission(permissions.BasePermission):
    """
    Unified role-based permission class.

    Usage examples:
        # Pass the base class (DRF will instantiate with no args)
        permission_classes = [permissions.IsAuthenticated, RolePermission]

        # Or use a subclass with roles configured
        permission_classes = [
            permissions.IsAuthenticated,
            IsStudent
        ]
    """

    allowed_roles: list[str] = []
    allow_read_only: bool = False

    def has_permission(self, request, view):
        """
        Check if the user has permission based on role and request method.
        """
        # Always allow safe methods if allow_read_only is True
        if self.allow_read_only and request.method in permissions.SAFE_METHODS:
            return True

        if not request.user or not request.user.is_authenticated:
            return False

        # Admin override: staff/superuser always allowed
        if getattr(request.user, "is_staff", False) or getattr(request.user, "is_superuser", False):
            return True

        # ✅ Check role field directly
        role = getattr(request.user, "role", None)
        if role in self.allowed_roles:
            return True

        return False

    def __str__(self):
        return f"RolePermission(roles={self.allowed_roles}, read_only={self.allow_read_only})"


# ✅ Backwards-compatible individual permissions using class attributes
class IsInstructor(RolePermission):
    """Permission class for instructors only."""
    allowed_roles = ["instructor"]


class IsStudent(RolePermission):
    """Permission class for students only."""
    allowed_roles = ["student"]


class IsAdmin(RolePermission):
    """Permission class for admins only."""
    allowed_roles = ["admin"]


class ReadOnly(RolePermission):
    """Permission class that allows read-only access for all authenticated users."""
    allow_read_only = True
