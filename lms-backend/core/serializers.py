from rest_framework import serializers
from core.models import Enrollment
from accounts.models import CustomUser  # ✅ use CustomUser consistently
from courses.models import Course


class EnrollmentSerializer(serializers.ModelSerializer):
    """
    Serializer for Enrollment model.
    Provides clear JSON output for student, course, and instructor details.
    Ensures role-based data isolation while keeping nested fields read-only.
    """

    # Student details
    student_username = serializers.CharField(source="student.username", read_only=True)
    student_email = serializers.EmailField(source="student.email", read_only=True)

    # Course details
    course_title = serializers.CharField(source="course.title", read_only=True)
    course_description = serializers.CharField(source="course.description", read_only=True)

    # Instructor details (from course relation)
    instructor_username = serializers.CharField(source="course.instructor.username", read_only=True)
    instructor_email = serializers.EmailField(source="course.instructor.email", read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            "id",
            "student",              # set automatically in views for students
            "student_username",
            "student_email",
            "course",               # required when enrolling
            "course_title",
            "course_description",
            "instructor_username",
            "instructor_email",
            "created_at",
        ]
        read_only_fields = [
            "created_at",
            "student_username",
            "student_email",
            "course_title",
            "course_description",
            "instructor_username",
            "instructor_email",
        ]

    def to_representation(self, instance):
        """
        Override to_representation for efficiency:
        Ensures select_related optimizations in views are respected,
        and provides a clean, consistent JSON structure.
        """
        representation = super().to_representation(instance)

        # Ensure null safety for nested fields
        if not instance.student:
            representation["student_username"] = None
            representation["student_email"] = None
        if not instance.course:
            representation["course_title"] = None
            representation["course_description"] = None
            representation["instructor_username"] = None
            representation["instructor_email"] = None

        return representation
