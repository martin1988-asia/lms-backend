from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from assignments.models import Submission
from .models import Grade
from .serializers import GradeSerializer, SubmissionSerializer


class GradeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing grades.
    Role-based isolation:
    - Students: can view only their own grades.
    - Instructors: can view grades for their courses and create/update/delete grades.
    - Admins: can view/manage all grades.
    """
    serializer_class = GradeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not getattr(user, "role", None):
            return Grade.objects.none()

        if user.role == "student":
            return Grade.objects.filter(submission__student=user).select_related(
                "submission__student", "submission__assignment", "instructor"
            )
        elif user.role == "instructor":
            return Grade.objects.filter(submission__assignment__course__instructor=user).select_related(
                "submission__student", "submission__assignment", "instructor"
            )
        elif user.role == "admin":
            return Grade.objects.select_related(
                "submission__student", "submission__assignment", "instructor"
            )

        return Grade.objects.none()

    def create(self, request, *args, **kwargs):
        user = request.user
        if getattr(user, "role", None) not in ["instructor", "admin"]:
            return Response(
                {"detail": "Access denied. Only instructors or admins can create grades."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        Automatically set instructor to the logged-in user when creating a grade.
        """
        serializer.save(instructor=self.request.user)

    def perform_update(self, serializer):
        """
        Ensure instructor is always set to the logged-in user when updating a grade.
        """
        serializer.save(instructor=self.request.user)


class SubmissionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing submissions.
    Role-based isolation:
    - Students: can create and view their own submissions.
    - Instructors: can view submissions for their courses and update feedback/score.
    - Admins: can view/manage all submissions.
    """
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not getattr(user, "role", None):
            return Submission.objects.none()

        if user.role == "student":
            return Submission.objects.filter(student=user).select_related("student", "assignment")
        elif user.role == "instructor":
            return Submission.objects.filter(assignment__course__instructor=user).select_related("student", "assignment")
        elif user.role == "admin":
            return Submission.objects.select_related("student", "assignment")

        return Submission.objects.none()

    def create(self, request, *args, **kwargs):
        user = request.user
        if getattr(user, "role", None) != "student":
            raise PermissionDenied("Only students can create submissions.")
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        Automatically assign the logged-in student to the submission.
        """
        serializer.save(student=self.request.user)
