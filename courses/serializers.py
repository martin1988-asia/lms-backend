from rest_framework import serializers
from accounts.models import CustomUser
from .models import Course, Enrollment


class UserNestedSerializer(serializers.ModelSerializer):
    """
    Nested serializer to show basic user info (Courses).
    """
    class Meta:
        model = CustomUser
        fields = ("id", "username", "email", "role")
        ref_name = "CoursesUserNested"   # ✅ unique schema name to avoid conflicts


class CourseSerializer(serializers.ModelSerializer):
    instructor = UserNestedSerializer(read_only=True)

    class Meta:
        model = Course
        fields = ("id", "title", "description", "instructor", "created_at")
        read_only_fields = ("instructor", "created_at")  # ✅ prevents 400 errors


class EnrollmentSerializer(serializers.ModelSerializer):
    student = UserNestedSerializer(read_only=True)
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())

    class Meta:
        model = Enrollment
        fields = ("id", "student", "course", "date_enrolled")
        read_only_fields = ("student", "date_enrolled")  # ✅ prevents 400 errors
