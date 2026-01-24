from rest_framework.permissions import BasePermission, SAFE_METHODS


class ReadOnly(BasePermission):
    """
    Permission that allows read-only access (GET, HEAD, OPTIONS).
    """
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class IsAdmin(BasePermission):
    """
    Permission that allows access only to admin users.
    Uses CustomUser.is_admin() helper for consistency.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin()


class IsTeacher(BasePermission):
    """
    Permission that allows access only to instructors.
    Uses CustomUser.is_instructor() helper for consistency.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_instructor()


class IsStudent(BasePermission):
    """
    Permission that allows access only to students.
    Uses CustomUser.is_student() helper for consistency.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_student()
