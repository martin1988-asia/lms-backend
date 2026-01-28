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
        if not getattr(user, "role", None):
            return Assignment.objects.none()

        if user.role == "instructor":
            return Assignment.objects.filter(course__instructor=user).select_related("course", "module")
        elif user.role == "student":
            return Assignment.objects.filter(course__enrollments__student=user).select_related("course", "module")
        elif user.role == "admin":
            return Assignment.objects.select_related("course", "module")

        return Assignment.objects.none()

    def create(self, request, *args, **kwargs):
        user = request.user
        if getattr(user, "role", None) != "instructor":
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
        serializer.save(due_date=due_date, created_by=self.request.user)


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
        if not getattr(user, "role", None):
            return Submission.objects.none()

        if user.role == "student":
            return Submission.objects.filter(student=user).select_related("assignment", "student")
        elif user.role == "instructor":
            return Submission.objects.filter(assignment__course__instructor=user).select_related("assignment", "student")
        elif user.role == "admin":
            return Submission.objects.select_related("assignment", "student")

        return Submission.objects.none()

    def create(self, request, *args, **kwargs):
        user = request.user
        if getattr(user, "role", None) != "student":
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
