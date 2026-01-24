from django.urls import path
from .views import AnalyticsViewSet

analytics_list = AnalyticsViewSet.as_view({"get": "list"})
student_analytics = AnalyticsViewSet.as_view({"get": "student"})
instructor_analytics = AnalyticsViewSet.as_view({"get": "instructor"})
admin_analytics = AnalyticsViewSet.as_view({"get": "admin"})
overview_analytics = AnalyticsViewSet.as_view({"get": "overview"})
course_analytics = AnalyticsViewSet.as_view({"get": "course"})

urlpatterns = [
    path("", analytics_list, name="analytics-list"),  # auto-detect role
    path("student/", student_analytics, name="student-analytics"),
    path("instructor/", instructor_analytics, name="instructor-analytics"),
    path("admin/", admin_analytics, name="admin-analytics"),
    path("overview/", overview_analytics, name="overview-analytics"),
    path("course/<int:pk>/", course_analytics, name="course-analytics"),
]
