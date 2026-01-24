from rest_framework import viewsets, permissions
from .models import Grade
from .serializers import GradeSerializer
from accounts.permissions import RolePermission


class InstructorOrAdminPermission(RolePermission):
    allowed_roles = ["instructor", "admin"]
    allow_read_only = True


class StudentInstructorAdminPermission(RolePermission):
    allowed_roles = ["student", "instructor", "admin"]
    allow_read_only = True


class GradeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing grades.
    - Instructors and admins can create/update/delete grades.
    - Students can view only their own grades.
    - Instructors can view grades for their courses.
    - Admins can view all grades.
    """
    queryset = Grade.objects.all()  # ✅ required for ModelViewSet
    serializer_class = GradeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "role"):
            if user.role == "student":
                # Students only see their own grades
                return Grade.objects.filter(submission__student=user)
            elif user.role == "instructor":
                # Instructors see all grades for assignments in their courses
                return Grade.objects.filter(submission__assignment__course__instructor=user)
            elif user.role == "admin":
                # Admins see everything
                return Grade.objects.all()
        # Default: no grades
        return Grade.objects.none()

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [permissions.IsAuthenticated, StudentInstructorAdminPermission]
        else:
            permission_classes = [permissions.IsAuthenticated, InstructorOrAdminPermission]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        # ✅ automatically set instructor to logged-in user
        serializer.save(instructor=self.request.user)
