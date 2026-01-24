from django.urls import path
from .views import StudentDashboardView, InstructorDashboardView, AdminDashboardView

urlpatterns = [
    path("student/", StudentDashboardView.as_view(), name="api-student-dashboard"),
    path("instructor/", InstructorDashboardView.as_view(), name="api-instructor-dashboard"),
    path("admin/", AdminDashboardView.as_view(), name="api-admin-dashboard"),
]
