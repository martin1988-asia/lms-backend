from rest_framework import serializers
from core.models import Enrollment
from users.models import User
from courses.models import Course


class EnrollmentSerializer(serializers.ModelSerializer):
    """
    Serializer for Enrollment model.
    Ensures proper JSON output for student, course, and role-based data.
    """

    student_username = serializers.CharField(source="student.username", read_only=True)
    student_email = serializers.EmailField(source="student.email", read_only=True)
    course_title = serializers.CharField(source="course.title", read_only=True)
    course_description = serializers.CharField(source="course.description", read_only=True)
    instructor_username = serializers.CharField(source="course.instructor.username", read_only=True)
    instructor_email = serializers.EmailField(source="course.instructor.email", read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            "id",
            "student",
            "student_username",
            "student_email",
            "course",
            "course_title",
            "course_description",
            "instructor_username",
            "instructor_email",
            "created_at",
        ]
        read_only_fields = ["created_at"]
