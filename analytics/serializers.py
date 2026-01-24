from rest_framework import serializers


class GPATrendSerializer(serializers.Serializer):
    assignment = serializers.CharField(help_text="Assignment title")
    score = serializers.FloatField(min_value=0, allow_null=True, help_text="Score achieved for the assignment")

    class Meta:
        ref_name = "AnalyticsGPATrend"   # ✅ unique schema name


class StudentAnalyticsSerializer(serializers.Serializer):
    gpa = serializers.FloatField(min_value=0, allow_null=True, help_text="Student GPA based on graded submissions")
    completion_rate = serializers.FloatField(min_value=0, allow_null=True, help_text="Percentage of assignments completed")
    grades_count = serializers.IntegerField(min_value=0, default=0, help_text="Total number of grades received")
    assignments_count = serializers.IntegerField(min_value=0, default=0, help_text="Total number of assignments assigned")
    grade_distribution = serializers.DictField(
        child=serializers.IntegerField(min_value=0, default=0),
        default=dict,
        help_text="Counts of grades by letter (A, B, C, etc.)"
    )
    gpa_trend = GPATrendSerializer(many=True, required=False, default=list, help_text="Trend of GPA across assignments")

    class Meta:
        ref_name = "AnalyticsStudent"   # ✅ unique schema name


class PerformanceTrendSerializer(serializers.Serializer):
    course = serializers.CharField(help_text="Course title")
    average_score = serializers.FloatField(min_value=0, allow_null=True, help_text="Average score for the course")

    class Meta:
        ref_name = "AnalyticsPerformanceTrend"   # ✅ unique schema name


class InstructorAnalyticsSerializer(serializers.Serializer):
    courses_taught = serializers.IntegerField(min_value=0, default=0, help_text="Number of courses taught")
    assignments_created = serializers.IntegerField(min_value=0, default=0, help_text="Number of assignments created")
    submissions_received = serializers.IntegerField(min_value=0, default=0, help_text="Number of submissions received")
    grades_given = serializers.IntegerField(min_value=0, default=0, help_text="Number of grades given")
    course_performance = serializers.DictField(
        child=serializers.FloatField(min_value=0, allow_null=True),
        default=dict,
        help_text="Average score per course"
    )
    submission_timeliness_rate = serializers.FloatField(min_value=0, allow_null=True, help_text="Percentage of submissions on time")
    performance_trend = PerformanceTrendSerializer(many=True, required=False, default=list, help_text="Performance trend per course")

    class Meta:
        ref_name = "AnalyticsInstructor"   # ✅ unique schema name


class EnrollmentTrendSerializer(serializers.Serializer):
    course = serializers.CharField(help_text="Course title")
    enrollment_count = serializers.IntegerField(min_value=0, default=0, help_text="Number of students enrolled in the course")

    class Meta:
        ref_name = "AnalyticsEnrollmentTrend"   # ✅ unique schema name


class AdminAnalyticsSerializer(serializers.Serializer):
    total_courses = serializers.IntegerField(min_value=0, default=0, help_text="Total number of courses in the system")
    total_students = serializers.IntegerField(min_value=0, default=0, help_text="Total number of enrolled students")
    total_instructors = serializers.IntegerField(min_value=0, default=0, help_text="Total number of instructors")
    total_submissions = serializers.IntegerField(min_value=0, default=0, help_text="Total number of submissions across all courses")
    total_grades = serializers.IntegerField(min_value=0, default=0, help_text="Total number of grades given across all courses")
    global_gpa = serializers.FloatField(min_value=0, allow_null=True, help_text="Global GPA across all students")
    grade_distribution = serializers.DictField(
        child=serializers.IntegerField(min_value=0, default=0),
        default=dict,
        help_text="Counts of grades by letter"
    )
    course_enrollment_stats = serializers.DictField(
        child=serializers.IntegerField(min_value=0, default=0),
        default=dict,
        help_text="Enrollment count per course"
    )
    enrollment_trend = EnrollmentTrendSerializer(many=True, required=False, default=list, help_text="Enrollment trend per course")

    class Meta:
        ref_name = "AnalyticsAdmin"   # ✅ unique schema name
