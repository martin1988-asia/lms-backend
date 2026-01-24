from rest_framework import serializers
from accounts.models import CustomUser
from .models import Assignment, Submission


class UserNestedSerializer(serializers.ModelSerializer):
    """
    Nested serializer for displaying basic user info (Assignments).
    """
    class Meta:
        model = CustomUser
        fields = ("id", "username", "email", "role")
        ref_name = "AssignmentsUserNested"   # ✅ unique schema name to avoid conflicts


class AssignmentSerializer(serializers.ModelSerializer):
    """
    Serializer for assignments.
    Includes course title, module info, and creator details.
    """
    course_title = serializers.CharField(source="course.title", read_only=True)
    module_title = serializers.CharField(source="module.title", read_only=True)
    created_by = UserNestedSerializer(read_only=True)

    class Meta:
        model = Assignment
        fields = (
            "id",
            "title",
            "description",
            "due_date",
            "created_at",
            "course",
            "course_title",
            "module",
            "module_title",
            "created_by",
        )
        read_only_fields = ("created_by", "created_at")  # ✅ prevents 400 errors

    def create(self, validated_data):
        """
        Automatically set created_by to the authenticated user.
        """
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["created_by"] = request.user
        return super().create(validated_data)


class SubmissionSerializer(serializers.ModelSerializer):
    """
    Serializer for submissions.
    Student is set automatically, assignment is passed as a PK.
    """
    student = UserNestedSerializer(read_only=True)
    assignment = serializers.PrimaryKeyRelatedField(queryset=Assignment.objects.all())

    class Meta:
        model = Submission
        fields = (
            "id",
            "student",
            "assignment",
            "content",
            "submitted_at",
            "feedback",
        )
        read_only_fields = ("student", "submitted_at", "feedback")  # ✅ prevents 400 errors

    def create(self, validated_data):
        """
        Automatically set student to the authenticated user.
        """
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["student"] = request.user
        return super().create(validated_data)
