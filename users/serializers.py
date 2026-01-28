from rest_framework import serializers
from accounts.models import CustomUser, Profile
from courses.models import Course, Module
from assignments.models import Assignment, Submission


class ProfileSerializer(serializers.ModelSerializer):
    """
    Nested serializer for user profile information (Users).
    """
    class Meta:
        model = Profile
        fields = ["bio", "avatar"]
        ref_name = "UsersProfile"   # ✅ unique schema name


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for CustomUser.
    Includes nested profile information.
    """
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
            "role",
            "is_staff",
            "is_superuser",
            "profile",
        ]
        ref_name = "UsersCustomUser"   # ✅ unique schema name

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if not getattr(instance, "profile", None):
            representation["profile"] = None
        return representation


class CourseSerializer(serializers.ModelSerializer):
    """
    Serializer for Course.
    Includes instructor username for clarity.
    """
    instructor_name = serializers.CharField(source="instructor.username", read_only=True)

    class Meta:
        model = Course
        fields = ["id", "title", "description", "instructor", "instructor_name"]
        ref_name = "UsersCourse"   # ✅ unique schema name


class ModuleSerializer(serializers.ModelSerializer):
    """
    Serializer for Module.
    Includes course title for clarity.
    """
    course_title = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = Module
        fields = ["id", "course", "course_title", "title", "content"]
        ref_name = "UsersModule"   # ✅ unique schema name


class AssignmentSerializer(serializers.ModelSerializer):
    """
    Serializer for Assignment.
    Includes module title and creator username for clarity.
    """
    module_title = serializers.CharField(source="module.title", read_only=True)
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = Assignment
        fields = [
            "id",
            "module",
            "module_title",
            "title",
            "description",
            "due_date",
            "created_by",
            "created_by_name",
        ]
        ref_name = "UsersAssignment"   # ✅ unique schema name


class SubmissionSerializer(serializers.ModelSerializer):
    """
    Serializer for Submission.
    Includes assignment title and student username for clarity.
    """
    assignment_title = serializers.CharField(source="assignment.title", read_only=True)
    student_name = serializers.CharField(source="student.username", read_only=True)

    class Meta:
        model = Submission
        fields = [
            "id",
            "assignment",
            "assignment_title",
            "student",
            "student_name",
            "content",
            "submitted_at",
            "grade",
        ]
        ref_name = "UsersSubmission"   # ✅ unique schema name
