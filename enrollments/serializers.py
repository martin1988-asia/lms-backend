from rest_framework import serializers
from accounts.models import CustomUser
from courses.models import Course
from .models import Enrollment


class UserNestedSerializer(serializers.ModelSerializer):
    """
    Nested serializer for basic student info (Enrollments).
    """
    class Meta:
        model = CustomUser
        fields = ("id", "username", "email", "role")
        ref_name = "EnrollmentsUserNested"   # ✅ unique schema name


class CourseNestedSerializer(serializers.ModelSerializer):
    """
    Nested serializer for basic course info (Enrollments).
    """
    class Meta:
        model = Course
        fields = ("id", "title", "description")
        ref_name = "EnrollmentsCourseNested"   # ✅ unique schema name


class EnrollmentSerializer(serializers.ModelSerializer):
    """
    Serializer for enrollments.
    Includes nested student and course details.
    """
    student = UserNestedSerializer(read_only=True)
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    course_detail = CourseNestedSerializer(source="course", read_only=True)

    # ✅ Add safe string fields for clarity
    student_username = serializers.CharField(source="student.username", read_only=True)
    course_title = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = Enrollment
        fields = (
            "id",
            "student",
            "student_username",
            "course",
            "course_title",
            "course_detail",
            "enrolled_at",
        )
        read_only_fields = ("student", "enrolled_at")

    def validate(self, data):
        """
        Prevent duplicate enrollments at the serializer level.
        """
        request = self.context.get("request")
        student = request.user if request and hasattr(request, "user") else None
        course = data.get("course")

        if student and course:
            if Enrollment.objects.filter(student=student, course=course).exists():
                raise serializers.ValidationError("You are already enrolled in this course.")
        return data

    def create(self, validated_data):
        """
        Automatically set student to the logged-in user.
        """
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["student"] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Ensure student is always set to the logged-in user on update.
        """
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["student"] = request.user
        return super().update(instance, validated_data)
