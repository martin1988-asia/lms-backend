from django.urls import path
from .views import AnalyticsLogViewSet   # ✅ corrected import

# Map viewset actions to endpoints
analytics_list = AnalyticsLogViewSet.as_view({"get": "list"})
student_analytics = AnalyticsLogViewSet.as_view({"get": "student"})
instructor_analytics = AnalyticsLogViewSet.as_view({"get": "instructor"})
admin_analytics = AnalyticsLogViewSet.as_view({"get": "admin"})
overview_analytics = AnalyticsLogViewSet.as_view({"get": "overview"})
course_analytics = AnalyticsLogViewSet.as_view({"get": "course"})

urlpatterns = [
    # Default analytics list (auto-detect role)
    path("", analytics_list, name="analytics-list"),

    # Role-specific analytics
    path("student/", student_analytics, name="student-analytics"),
    path("instructor/", instructor_analytics, name="instructor-analytics"),
    path("admin/", admin_analytics, name="admin-analytics"),

    # Extra analytics endpoints
    path("overview/", overview_analytics, name="overview-analytics"),
    path("course/<int:pk>/", course_analytics, name="course-analytics"),

    # ✅ Aliases under api/ for compatibility with tests
    path("api/student/", student_analytics, name="api-student-analytics"),
    path("api/instructor/", instructor_analytics, name="api-instructor-analytics"),
    path("api/admin/", admin_analytics, name="api-admin-analytics"),
    path("api/overview/", overview_analytics, name="api-overview-analytics"),
    path("api/course/<int:pk>/", course_analytics, name="api-course-analytics"),
]
