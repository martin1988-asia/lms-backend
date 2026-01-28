from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.routers import DefaultRouter
from django.http import HttpResponse

from accounts.views import CustomTokenObtainPairView, SignupView
from users.views import UserViewSet, ModuleViewSet
from courses.views import CourseViewSet, EnrollmentViewSet
from assignments.views import AssignmentViewSet
from grades.views import GradeViewSet, SubmissionViewSet
from dashboard.views import StudentDashboardView, InstructorDashboardView, AdminDashboardView

# For password reset
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetCompleteView,
)

schema_view = get_schema_view(
    openapi.Info(
        title="LMS API",
        default_version="v1",
        description="API documentation for the Learning Management System",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()
router.include_format_suffixes = False
router.register(r"users", UserViewSet, basename="user")
router.register(r"courses", CourseViewSet, basename="course")
router.register(r"enrollments", EnrollmentViewSet, basename="enrollment")
router.register(r"assignments", AssignmentViewSet, basename="assignment")
router.register(r"submissions", SubmissionViewSet, basename="submission")
router.register(r"grades", GradeViewSet, basename="grade")
router.register(r"modules", ModuleViewSet, basename="module")

def home(request):
    html = """
    <html>
      <head>
        <meta http-equiv="refresh" content="3;url=/swagger/" />
      </head>
      <body style="font-family: Arial; text-align: center; margin-top: 50px;">
        <h2>Welcome to Martin's backend</h2>
        <p>Redirecting to <a href="/swagger/">Swagger docs</a> in 3 seconds...</p>
      </body>
    </html>
    """
    return HttpResponse(html)

urlpatterns = [
    path("", home, name="home"),

    # ✅ Admin site
    path("admin/", admin.site.urls),

    # Accounts endpoints
    path("accounts/", include("accounts.urls")),
    path("auth/", include("accounts.urls")),
    path("api/accounts/", include("accounts.urls")),
    path("api/auth/", include("accounts.urls")),

    # Other apps
    path("analytics/", include("analytics.urls")),
    path("users/", include("users.urls")),

    # Dashboard endpoints
    path("dashboard/student/", StudentDashboardView.as_view(), name="student-dashboard"),
    path("dashboard/instructor/", InstructorDashboardView.as_view(), name="instructor-dashboard"),
    path("dashboard/admin/", AdminDashboardView.as_view(), name="admin-dashboard"),

    # API-prefixed dashboard endpoints
    path("api/dashboard/student/", StudentDashboardView.as_view(), name="api-student-dashboard"),
    path("api/dashboard/instructor/", InstructorDashboardView.as_view(), name="api-instructor-dashboard"),
    path("api/dashboard/admin/", AdminDashboardView.as_view(), name="api-admin-dashboard"),

    # Auth
    path("auth/login/", CustomTokenObtainPairView.as_view(), name="custom_token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="custom_token_refresh"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/signup/", SignupView.as_view(), name="signup"),

    # Forgot password (reset flow)
    path("auth/password-reset/", PasswordResetView.as_view(), name="password_reset"),
    path("auth/password-reset/done/", PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("auth/password-reset-confirm/<uidb64>/<token>/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("auth/password-reset-complete/", PasswordResetCompleteView.as_view(), name="password_reset_complete"),

    # Extra JWT endpoints
    path("api/auth/token/", CustomTokenObtainPairView.as_view(), name="api_auth_token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="api_auth_token_refresh"),
    path("api/token/", CustomTokenObtainPairView.as_view(), name="api_token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="api_token_refresh"),

    # Swagger
    path("swagger.json", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger.yaml", schema_view.without_ui(cache_timeout=0), name="schema-yaml"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),

    # ✅ Router endpoints under /api/
    path("api/", include(router.urls)),
]
