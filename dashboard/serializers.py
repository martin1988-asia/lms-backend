from rest_framework import serializers


# ------------------ Shared / Nested Serializers ------------------

class GradeDistributionSerializer(serializers.Serializer):
    grade = serializers.FloatField()
    count = serializers.IntegerField()


class TrendPointSerializer(serializers.Serializer):
    submitted_at = serializers.DateTimeField()
    grade = serializers.FloatField()


class ModuleCompletionSerializer(serializers.Serializer):
    module__title = serializers.CharField()
    total = serializers.IntegerField()
    completed = serializers.IntegerField()


class CoursePerformanceSerializer(serializers.Serializer):
    course__title = serializers.CharField()
    avg_grade = serializers.FloatField()


class EnrollmentTrendSerializer(serializers.Serializer):
    date_enrolled = serializers.DateField()
    count = serializers.IntegerField()


# ------------------ Dashboard Serializers ------------------

class StudentDashboardSerializer(serializers.Serializer):
    grades_count = serializers.IntegerField()
    assignments_count = serializers.IntegerField()
    gpa = serializers.FloatField()
    completion_rate = serializers.FloatField()
    grade_distribution = GradeDistributionSerializer(many=True)
    gpa_trend = TrendPointSerializer(many=True)
    module_completion = ModuleCompletionSerializer(many=True)


class InstructorDashboardSerializer(serializers.Serializer):
    courses_taught = serializers.IntegerField()
    assignments_created = serializers.IntegerField()
    submissions_received = serializers.IntegerField()
    grades_given = serializers.IntegerField()
    course_performance = CoursePerformanceSerializer(many=True)
    performance_trends = TrendPointSerializer(many=True)


class AdminDashboardSerializer(serializers.Serializer):
    total_courses = serializers.IntegerField()
    total_students = serializers.IntegerField()
    total_instructors = serializers.IntegerField()
    total_submissions = serializers.IntegerField()
    total_grades = serializers.IntegerField()
    global_gpa = serializers.FloatField()
    grade_distribution = GradeDistributionSerializer(many=True)
    enrollment_trends = EnrollmentTrendSerializer(many=True)
