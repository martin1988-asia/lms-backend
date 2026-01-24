from rest_framework import viewsets, permissions
from .models import Enrollment
from .serializers import EnrollmentSerializer
from accounts.permissions import RolePermission


class StudentPermission(RolePermission):
    allowed_roles = ["student"]
    allow_read_only = True


class InstructorOrAdminPermission(RolePermission):
    allowed_roles = ["instructor", "admin"]
    allow_read_only = True


class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing course enrollments.
    - Students can enroll themselves in courses.
    - Instructors and admins can view/manage enrollments.
    - Authenticated users can list/retrieve enrollments.
    """
    serializer_class = EnrollmentSerializer

    def get_queryset(self):
        """
        Role-based filtering:
        - Students see only their enrollments.
        - Instructors see enrollments for their courses.
        - Admins see all enrollments.
        """
        user = self.request.user
        if hasattr(user, "role"):
            if user.role == "student":
                return Enrollment.objects.filter(student=user)
            elif user.role == "instructor":
                return Enrollment.objects.filter(course__instructor=user)
            elif user.role == "admin":
                return Enrollment.objects.all()
        return Enrollment.objects.none()

    def get_permissions(self):
        """
        Role-based permissions:
        - Students can create enrollments.
        - Instructors/Admins can view/manage enrollments.
        - All authenticated users can list/retrieve.
        """
        if self.action in ["list", "retrieve"]:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == "create":
            # Only students can enroll themselves
            permission_classes = [permissions.IsAuthenticated, StudentPermission]
        else:
            # update/delete → instructors or admins
            permission_classes = [permissions.IsAuthenticated, InstructorOrAdminPermission]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """
        Automatically set the student to the logged-in user when creating an enrollment.
        """
        serializer.save(student=self.request.user)
