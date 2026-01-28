from rest_framework import serializers
from accounts.models import CustomUser
from assignments.models import Submission, Assignment
from .models import Grade


class UserNestedSerializer(serializers.ModelSerializer):
    """
    Nested serializer for basic user info.
    Used in Grade and Submission serializers to avoid duplication.
    """
    class Meta:
        model = CustomUser
        fields = ("id", "username", "email", "role")
        ref_name = "GradesUserNested"   # ✅ unique schema name to avoid conflicts


class AssignmentNestedSerializer(serializers.ModelSerializer):
    """
    Nested serializer for basic assignment info.
    """
    class Meta:
        model = Assignment
        fields = ("id", "title", "due_date")
        ref_name = "GradesAssignmentNested"   # ✅ unique schema name to avoid conflicts


class SubmissionNestedSerializer(serializers.ModelSerializer):
    """
    Nested serializer for submission info, including student and assignment.
    """
    student = UserNestedSerializer(read_only=True)
    assignment = AssignmentNestedSerializer(read_only=True)

    class Meta:
        model = Submission
        fields = ("id", "student", "assignment", "content", "submitted_at")
        ref_name = "GradesSubmissionNested"   # ✅ unique schema name to avoid conflicts

    def to_representation(self, instance):
        """
        Ensure null safety for nested fields.
        """
        representation = super().to_representation(instance)
        if not getattr(instance, "student", None):
            representation["student"] = None
        if not getattr(instance, "assignment", None):
            representation["assignment"] = None
        return representation


class SubmissionSerializer(serializers.ModelSerializer):
    """
    Full serializer for submissions, allowing instructors to grade.
    """
    student = UserNestedSerializer(read_only=True)
    assignment = AssignmentNestedSerializer(read_only=True)

    class Meta:
        model = Submission
        fields = [
            "id",
            "student",
            "assignment",
            "content",
            "submitted_at",
            "feedback",
            "grade",   # ✅ matches Submission model field
        ]
        read_only_fields = ["id", "student", "assignment", "submitted_at"]


class GradeSerializer(serializers.ModelSerializer):
    """
    Serializer for grades.
    Includes nested instructor, submission details, and student info.
    """
    instructor = UserNestedSerializer(read_only=True)
    submission = serializers.PrimaryKeyRelatedField(queryset=Submission.objects.all())
    submission_detail = SubmissionNestedSerializer(source="submission", read_only=True)
    student = serializers.SerializerMethodField()   # ✅ nested student field

    class Meta:
        model = Grade
        fields = (
            "id",
            "submission",
            "submission_detail",
            "student",
            "instructor",
            "score",          # ✅ corrected to match Grade model
            "letter",
            "feedback",
            "graded_at",
        )
        read_only_fields = ("instructor", "graded_at")

    def get_student(self, obj):
        """
        Return student info from the related submission.
        """
        if obj.submission and getattr(obj.submission, "student", None):
            return {
                "id": obj.submission.student.id,
                "email": obj.submission.student.email,
                "username": obj.submission.student.username,
                "role": obj.submission.student.role,
            }
        return None

    def validate(self, data):
        """
        Prevent duplicate grading of the same submission.
        """
        submission = data.get("submission")
        if submission and Grade.objects.filter(submission=submission).exists():
            raise serializers.ValidationError(
                {"non_field_errors": ["This submission has already been graded."]}
            )
        return data

    def create(self, validated_data):
        """
        Automatically set instructor to the logged-in user.
        """
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            validated_data["instructor"] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Ensure instructor is always set to the logged-in user on update.
        """
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            validated_data["instructor"] = request.user
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """
        Ensure null safety for nested fields.
        """
        representation = super().to_representation(instance)
        if not getattr(instance, "submission", None):
            representation["submission_detail"] = None
        if not getattr(instance, "instructor", None):
            representation["instructor"] = None
        if not representation.get("student"):
            representation["student"] = None
        return representation
