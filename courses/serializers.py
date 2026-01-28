from rest_framework import serializers
from accounts.models import CustomUser
from .models import Course, Enrollment


class UserNestedSerializer(serializers.ModelSerializer):
    """
    Nested serializer to show basic user info.
    Used in Course and Enrollment serializers to avoid duplication.
    """
    class Meta:
        model = CustomUser
        fields = ("id", "username", "email", "role")
        ref_name = "CoursesUserNested"   # ✅ unique schema name to avoid conflicts


class CourseSerializer(serializers.ModelSerializer):
    """
    Serializer for Course model.
    Includes instructor details via nested serializer.
    """
    instructor = UserNestedSerializer(read_only=True)

    class Meta:
        model = Course
        fields = ("id", "title", "description", "instructor", "created_at")
        read_only_fields = ("instructor", "created_at")
        ref_name = "CoursesCourse"   # ✅ unique schema name

    def to_representation(self, instance):
        """
        Ensure null safety for nested instructor fields.
        """
        representation = super().to_representation(instance)
        if not getattr(instance, "instructor", None):
            representation["instructor"] = None
        return representation


class EnrollmentSerializer(serializers.ModelSerializer):
    """
    Serializer for Enrollment model.
    Student is set automatically, course is passed as a PK.
    """
    student = UserNestedSerializer(read_only=True)
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    course_detail = serializers.SerializerMethodField()  # ✅ add nested course info

    class Meta:
        model = Enrollment
        fields = ("id", "student", "course", "course_detail", "date_enrolled")
        read_only_fields = ("student", "date_enrolled")
        ref_name = "CoursesEnrollment"   # ✅ unique schema name

    def get_course_detail(self, obj):
        """
        Return nested course info for clarity.
        """
        if obj.course:
            return {
                "id": obj.course.id,
                "title": obj.course.title,
                "description": obj.course.description,
            }
        return None

    def validate(self, data):
        """
        Prevent duplicate enrollments for the same student and course.
        """
        request = self.context.get("request")
        student = request.user if request and request.user.is_authenticated else None
        course = data.get("course")

        if student and course:
            if Enrollment.objects.filter(student=student, course=course).exists():
                raise serializers.ValidationError(
                    {"non_field_errors": ["You are already enrolled in this course."]}
                )
        return data

    def create(self, validated_data):
        """
        Automatically set student to the authenticated user if role is student.
        """
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            validated_data["student"] = request.user
        return super().create(validated_data)

    def to_representation(self, instance):
        """
        Ensure null safety for nested fields.
        """
        representation = super().to_representation(instance)
        if not getattr(instance, "course", None):
            representation["course"] = None
        if not getattr(instance, "student", None):
            representation["student"] = None
        return representation
