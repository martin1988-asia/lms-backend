from rest_framework import serializers
from accounts.models import CustomUser
from assignments.models import Submission, Assignment
from .models import Grade


class UserNestedSerializer(serializers.ModelSerializer):
    """
    Nested serializer for basic user info (Grades).
    """
    class Meta:
        model = CustomUser
        fields = ("id", "username", "email", "role")
        ref_name = "GradesUserNested"   # ✅ unique schema name


class AssignmentNestedSerializer(serializers.ModelSerializer):
    """
    Nested serializer for basic assignment info (Grades).
    """
    class Meta:
        model = Assignment
        fields = ("id", "title", "due_date")
        ref_name = "GradesAssignmentNested"   # ✅ unique schema name


class SubmissionNestedSerializer(serializers.ModelSerializer):
    """
    Nested serializer for submission info, including student and assignment (Grades).
    """
    student = UserNestedSerializer(read_only=True)
    assignment = AssignmentNestedSerializer(read_only=True)

    class Meta:
        model = Submission
        fields = ("id", "student", "assignment", "content", "submitted_at")
        ref_name = "GradesSubmissionNested"   # ✅ unique schema name


class GradeSerializer(serializers.ModelSerializer):
    """
    Serializer for grades.
    Includes nested instructor and submission details.
    """
    instructor = UserNestedSerializer(read_only=True)
    submission = serializers.PrimaryKeyRelatedField(queryset=Submission.objects.all())
    submission_detail = SubmissionNestedSerializer(source="submission", read_only=True)

    class Meta:
        model = Grade
        fields = (
            "id",
            "submission",
            "submission_detail",
            "instructor",
            "score",
            "letter",
            "feedback",
            "graded_at",
        )
        read_only_fields = ("instructor", "graded_at")  # ✅ prevents 400 errors

    def validate(self, data):
        """
        Prevent duplicate grading of the same submission.
        """
        submission = data.get("submission")
        if submission and Grade.objects.filter(submission=submission).exists():
            raise serializers.ValidationError("This submission has already been graded.")
        return data

    def create(self, validated_data):
        """
        Automatically set instructor to the logged-in user.
        """
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["instructor"] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Ensure instructor is always set to the logged-in user on update.
        """
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["instructor"] = request.user
        return super().update(instance, validated_data)
