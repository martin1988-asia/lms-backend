from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdmin(BasePermission):
    """
    Allow only admin users (role = admin).
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "admin"


class IsTeacher(BasePermission):
    """
    Allow only teacher users (role = teacher).
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "teacher"


class IsStudent(BasePermission):
    """
    Allow only student users (role = student).
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "student"


class ReadOnly(BasePermission):
    """
    Allow read-only access (GET, HEAD, OPTIONS).
    """
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
