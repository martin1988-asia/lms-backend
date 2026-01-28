from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from core.models import Enrollment
from core.serializers import EnrollmentSerializer


class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing enrollments with strict role-based isolation:
    - Students: can enroll themselves in courses and view their own enrollments
    - Instructors: can view enrollments for courses they teach
    - Admins: can view/manage all enrollments
    """
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, "role"):
            return Enrollment.objects.none()

        if user.role == "student":
            # Students only see their own enrollments
            return Enrollment.objects.filter(student=user).select_related("course", "student")
        elif user.role == "instructor":
            # Instructors see enrollments for their courses
            return Enrollment.objects.filter(course__instructor=user).select_related("course", "student")
        elif user.role == "admin":
            # Admins see all enrollments
            return Enrollment.objects.select_related("course", "student")

        return Enrollment.objects.none()

    def create(self, request, *args, **kwargs):
        user = request.user
        if not hasattr(user, "role"):
            return Response({"detail": "Access denied."}, status=status.HTTP_403_FORBIDDEN)

        if user.role == "student":
            # Students can enroll themselves
            return super().create(request, *args, **kwargs)
        elif user.role == "instructor":
            return Response(
                {"detail": "Access denied. Instructors cannot directly enroll students here."},
                status=status.HTTP_403_FORBIDDEN,
            )
        elif user.role == "admin":
            # Admins can enroll any student
            return super().create(request, *args, **kwargs)

        return Response({"detail": "Access denied."}, status=status.HTTP_403_FORBIDDEN)

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == "student":
            serializer.save(student=user)
        else:
            serializer.save()

    @action(detail=True, methods=["get"])
    def detail(self, request, pk=None):
        """
        Custom action to fetch a single enrollment with role-based access.
        """
        enrollment = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(enrollment)
        return Response(serializer.data)
