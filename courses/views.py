from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import Course, Enrollment
from .serializers import CourseSerializer, EnrollmentSerializer
from accounts.models import CustomUser


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing courses.
    Role-based isolation:
    - Instructors: can create/update/delete courses they teach.
    - Students: can list/retrieve courses they are enrolled in.
    - Admins: can view/manage all courses.
    """
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, "role"):
            return Course.objects.none()

        if user.role == "instructor":
            return Course.objects.filter(instructor=user).select_related("instructor")
        elif user.role == "student":
            return Course.objects.filter(enrollments__student=user).select_related("instructor")
        elif user.role == "admin":
            return Course.objects.select_related("instructor")

        return Course.objects.none()

    def create(self, request, *args, **kwargs):
        user = request.user
        if not hasattr(user, "role") or user.role not in ["instructor", "admin"]:
            return Response(
                {"detail": "Access denied. Only instructors or admins can create courses."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        Automatically set the instructor to the logged-in user.
        """
        serializer.save(instructor=self.request.user)


class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing enrollments.
    Role-based isolation:
    - Students: can enroll themselves in courses.
    - Instructors: can view enrollments for their courses.
    - Admins: can view/manage all enrollments.
    """
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, "role"):
            return Enrollment.objects.none()

        if user.role == "student":
            return Enrollment.objects.filter(student=user).select_related("course", "student")
        elif user.role == "instructor":
            return Enrollment.objects.filter(course__instructor=user).select_related("course", "student")
        elif user.role == "admin":
            return Enrollment.objects.select_related("course", "student")

        return Enrollment.objects.none()

    def create(self, request, *args, **kwargs):
        user = request.user
        if not hasattr(user, "role"):
            return Response(
                {"detail": "Access denied."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if user.role == "student":
            # Students can enroll themselves
            return super().create(request, *args, **kwargs)

        elif user.role == "admin":
            # Admins can enroll any student by specifying student ID
            student_id = request.data.get("student")
            if not student_id:
                return Response(
                    {"student": "Admin must specify a student ID."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                student = CustomUser.objects.get(id=student_id, role="student")
            except CustomUser.DoesNotExist:
                return Response(
                    {"student": "Invalid student ID."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(student=student)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        else:
            # Instructors cannot enroll students directly
            raise PermissionDenied("Instructors cannot enroll students directly.")

    def perform_create(self, serializer):
        """
        Automatically assign the logged-in student to the enrollment.
        For admins, handled in create().
        """
        if getattr(self.request.user, "role", None) == "student":
            serializer.save(student=self.request.user)
