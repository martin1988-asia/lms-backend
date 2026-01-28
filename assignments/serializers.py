from rest_framework import serializers
from accounts.models import CustomUser
from .models import Assignment, Submission


class UserNestedSerializer(serializers.ModelSerializer):
    """
    Nested serializer for displaying basic user info.
    Used in Assignment and Submission serializers to avoid duplication.
    """
    class Meta:
        model = CustomUser
        fields = ("id", "username", "email", "role")
        ref_name = "AssignmentsUserNested"   # ✅ unique schema name


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
        read_only_fields = ("created_by", "created_at")
        ref_name = "AssignmentsAssignment"   # ✅ unique schema name

    def create(self, validated_data):
        """
        Automatically set the creator to the authenticated user.
        """
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            validated_data["created_by"] = request.user
        return super().create(validated_data)

    def to_representation(self, instance):
        """
        Ensure course/module titles are always present, even if null.
        """
        representation = super().to_representation(instance)
        representation["course_title"] = getattr(instance.course, "title", None)
        representation["module_title"] = getattr(instance.module, "title", None)
        return representation


class SubmissionSerializer(serializers.ModelSerializer):
    """
    Serializer for submissions.
    Student is set automatically, assignment is passed as a PK.
    """
    student = UserNestedSerializer(read_only=True)
    assignment_title = serializers.CharField(source="assignment.title", read_only=True)
    assignment = serializers.PrimaryKeyRelatedField(queryset=Assignment.objects.all())

    class Meta:
        model = Submission
        fields = (
            "id",
            "student",
            "assignment",
            "assignment_title",
            "content",
            "submitted_at",
            "feedback",
            "grade",   # ✅ include grade field from model
        )
        read_only_fields = ("student", "submitted_at", "feedback")
        ref_name = "AssignmentsSubmission"   # ✅ unique schema name

    def create(self, validated_data):
        """
        Automatically set the student to the authenticated user.
        """
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            validated_data["student"] = request.user
        return super().create(validated_data)

    def to_representation(self, instance):
        """
        Ensure assignment title is always present, even if null.
        """
        representation = super().to_representation(instance)
        representation["assignment_title"] = getattr(instance.assignment, "title", None)
        return representation
