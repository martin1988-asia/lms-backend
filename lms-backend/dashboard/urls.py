from django.urls import path
from .views import StudentDashboardView, InstructorDashboardView, AdminDashboardView

urlpatterns = [
    # Role-specific dashboards
    path("student/", StudentDashboardView.as_view(), name="student-dashboard"),
    path("instructor/", InstructorDashboardView.as_view(), name="instructor-dashboard"),
    path("admin/", AdminDashboardView.as_view(), name="admin-dashboard"),

    # ✅ Aliases under api/ for compatibility with tests
    path("api/student/", StudentDashboardView.as_view(), name="api-student-dashboard"),
    path("api/instructor/", InstructorDashboardView.as_view(), name="api-instructor-dashboard"),
    path("api/admin/", AdminDashboardView.as_view(), name="api-admin-dashboard"),
]
