from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from core.models import Enrollment
from core.serializers import EnrollmentSerializer


class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing enrollments with strict role-based isolation:
    - Students: only their own enrollments
    - Instructors: enrollments for courses they teach
    - Admins: all enrollments
    """
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "student":
            return Enrollment.objects.filter(student=user)
        elif user.role == "instructor":
            return Enrollment.objects.filter(course__instructor=user)
        elif user.role == "admin":
            return Enrollment.objects.all()
        return Enrollment.objects.none()

    def perform_create(self, serializer):
        """
        Enforce role-based creation rules:
        - Students: cannot create enrollments directly
        - Instructors: can enroll students into their own courses
        - Admins: can enroll any student into any course
        """
        user = self.request.user
        if user.role == "student":
            raise permissions.PermissionDenied("Students cannot create enrollments directly.")
        elif user.role == "instructor":
            course = serializer.validated_data.get("course")
            if course.instructor != user:
                raise permissions.PermissionDenied("You can only enroll students into your own courses.")
        serializer.save()

    @action(detail=True, methods=["get"])
    def detail(self, request, pk=None):
        """
        Custom action to fetch a single enrollment with role-based access.
        """
        enrollment = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(enrollment)
        return Response(serializer.data)
