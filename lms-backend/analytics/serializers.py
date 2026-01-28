# analytics/views.py
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import (
    StudentAnalyticsSerializer,
    InstructorAnalyticsSerializer,
    AdminAnalyticsSerializer,
)

class AnalyticsLogViewSet(viewsets.ViewSet):
    """
    A simple ViewSet that returns analytics data depending on the role.
    For now, it returns dummy/sample data — replace with real queries later.
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user

        # Example: choose serializer based on role
        if user.is_superuser:
            data = {
                "total_courses": 5,
                "total_students": 120,
                "total_instructors": 10,
                "total_submissions": 300,
                "total_grades": 280,
                "global_gpa": 3.4,
                "grade_distribution": {"A": 100, "B": 120, "C": 60},
                "course_enrollment_stats": {"Math": 40, "Science": 30},
                "enrollment_trend": [
                    {"course": "Math", "enrollment_count": 40},
                    {"course": "Science", "enrollment_count": 30},
                ],
            }
            serializer = AdminAnalyticsSerializer(data)
            return Response(serializer.data)

        elif hasattr(user, "is_instructor") and user.is_instructor:
            data = {
                "courses_taught": 2,
                "assignments_created": 10,
                "submissions_received": 80,
                "grades_given": 75,
                "course_performance": {"Math": 85.5, "Science": 78.2},
                "submission_timeliness_rate": 92.0,
                "performance_trend": [
                    {"course": "Math", "average_score": 85.5},
                    {"course": "Science", "average_score": 78.2},
                ],
            }
            serializer = InstructorAnalyticsSerializer(data)
            return Response(serializer.data)

        else:
            # Default: treat as student
            data = {
                "gpa": 3.2,
                "completion_rate": 88.0,
                "grades_count": 12,
                "assignments_count": 15,
                "grade_distribution": {"A": 5, "B": 4, "C": 3},
                "gpa_trend": [
                    {"assignment": "Homework 1", "score": 85},
                    {"assignment": "Homework 2", "score": 90},
                ],
            }
            serializer = StudentAnalyticsSerializer(data)
            return Response(serializer.data)
