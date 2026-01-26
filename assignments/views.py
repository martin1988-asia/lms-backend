from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.utils import timezone
from .models import Assignment, Submission
from .serializers import AssignmentSerializer, SubmissionSerializer


class AssignmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing assignments.
    Role-based isolation:
    - Instructors: can create/update/delete assignments for their courses.
    - Students: can list/retrieve assignments from courses they are enrolled in.
    - Admins: can view/manage all assignments.
    """
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, "role"):
            return Assignment.objects.none()

        if user.role == "instructor":
            # Instructors see assignments for their courses
            return Assignment.objects.filter(course__instructor=user).select_related("course")
        elif user.role == "student":
            # Students see assignments for courses they are enrolled in
            return Assignment.objects.filter(course__enrollments__student=user).select_related("course")
        elif user.role == "admin":
            # Admins see all assignments
            return Assignment.objects.select_related("course")

        return Assignment.objects.none()

    def create(self, request, *args, **kwargs):
        user = request.user
        if not hasattr(user, "role") or user.role != "instructor":
            return Response(
                {"detail": "Access denied. Only instructors can create assignments."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        Ensure due_date is timezone-aware before saving.
        """
        due_date = serializer.validated_data.get("due_date")
        if due_date and timezone.is_naive(due_date):
            due_date = timezone.make_aware(due_date)
        serializer.save(due_date=due_date)


class SubmissionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing submissions.
    Role-based isolation:
    - Students: can create/update their own submissions.
    - Instructors: can view submissions for their courses.
    - Admins: can view/manage all submissions.
    """
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, "role"):
            return Submission.objects.none()

        if user.role == "student":
            # Students only see their own submissions
            return Submission.objects.filter(student=user).select_related("assignment", "student")
        elif user.role == "instructor":
            # Instructors see submissions for their courses
            return Submission.objects.filter(assignment__course__instructor=user).select_related("assignment", "student")
        elif user.role == "admin":
            # Admins see all submissions
            return Submission.objects.select_related("assignment", "student")

        return Submission.objects.none()

    def create(self, request, *args, **kwargs):
        user = request.user
        if not hasattr(user, "role") or user.role != "student":
            return Response(
                {"detail": "Access denied. Only students can submit assignments."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        Automatically assign the logged-in student to the submission.
        """
        serializer.save(student=self.request.user)
