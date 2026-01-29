from django.contrib import admin
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.routers import DefaultRouter
from django.http import HttpResponse

#from accounts.views import CustomTokenObtainPairView, SignupView, me   # ✅ added me import
from users.views import UserViewSet, ModuleViewSet
from courses.views import CourseViewSet, EnrollmentViewSet
from assignments.views import AssignmentViewSet, SubmissionViewSet
from grades.views import GradeViewSet, SubmissionViewSet as GradeSubmissionViewSet
from dashboard.views import StudentDashboardView, InstructorDashboardView, AdminDashboardView


# ✅ Swagger schema view (public, no auth required)
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
    authentication_classes=[],
)

# ✅ Router mounted under /api/
router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"courses", CourseViewSet, basename="course")
router.register(r"enrollments", EnrollmentViewSet, basename="enrollment")
router.register(r"assignments", AssignmentViewSet, basename="assignment")
router.register(r"submissions", SubmissionViewSet, basename="submission")
router.register(r"grades", GradeViewSet, basename="grade")
router.register(r"modules", ModuleViewSet, basename="module")


# ✅ Simple home redirect
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
    # Admin
    path("admin/", admin.site.urls),

    # Home
    path("", home, name="home"),

    # Accounts + other apps
    path("users/", include("users.urls")),

    # Dashboards
    path("dashboard/student/", StudentDashboardView.as_view(), name="student-dashboard"),
    path("dashboard/instructor/", InstructorDashboardView.as_view(), name="instructor-dashboard"),
    path("dashboard/admin/", AdminDashboardView.as_view(), name="admin-dashboard"),

    # API router
    path("api/", include(router.urls)),

    # ✅ Auth endpoints under /api/auth/
    path("api/auth/login/", CustomTokenObtainPairView.as_view(), name="api_auth_login"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="api_auth_refresh"),
    path("api/auth/signup/", SignupView.as_view(), name="api_auth_signup"),
    path("api/auth/me/", me, name="api_auth_me"),   # ✅ added /auth/me route

    # ✅ Swagger / Redoc
    path("swagger.json", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger.yaml", schema_view.without_ui(cache_timeout=0), name="schema-yaml"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]