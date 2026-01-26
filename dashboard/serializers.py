from rest_framework import serializers


# ------------------ Dashboard Serializers ------------------

class StudentDashboardSerializer(serializers.Serializer):
    """
    Serializer for student dashboard data.
    Provides GPA, assignments count, grades count, and completion rate.
    """
    grades_count = serializers.IntegerField()
    assignments_count = serializers.IntegerField()
    gpa = serializers.FloatField()
    completion_rate = serializers.FloatField()


class InstructorDashboardSerializer(serializers.Serializer):
    """
    Serializer for instructor dashboard data.
    Provides teaching stats and course performance averages.
    """
    courses_taught = serializers.IntegerField()
    assignments_created = serializers.IntegerField()
    submissions_received = serializers.IntegerField()
    grades_given = serializers.IntegerField()
    # course_performance is returned as a dict {course_title: avg_score}
    course_performance = serializers.DictField(
        child=serializers.FloatField()
    )


class AdminDashboardSerializer(serializers.Serializer):
    """
    Serializer for admin dashboard data.
    Provides global stats across courses, users, submissions, and grades.
    """
    total_courses = serializers.IntegerField()
    total_students = serializers.IntegerField()
    total_instructors = serializers.IntegerField()
    total_submissions = serializers.IntegerField()
    total_grades = serializers.IntegerField()
    global_gpa = serializers.FloatField()
    # grade_distribution is returned as a dict {letter: count}
    grade_distribution = serializers.DictField(
        child=serializers.IntegerField()
    )
    # course_enrollment_stats is returned as a dict {course_title: enrollment_count}
    course_enrollment_stats = serializers.DictField(
        child=serializers.IntegerField()
    )
