from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    SignupView,
    ProfileViewSet,
    CustomUserViewSet,
    CustomTokenObtainPairView,
    ForgotPasswordView,          # ✅ custom forgot password view
    ResetPasswordConfirmView,    # ✅ custom reset confirm view
)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.http import JsonResponse

# ✅ Router setup
router = DefaultRouter()
router.include_format_suffixes = False
router.register(r"profile", ProfileViewSet, basename="profile")
router.register(r"users", CustomUserViewSet, basename="user")

# ✅ Swagger/OpenAPI schema view
schema_view = get_schema_view(
    openapi.Info(
        title="LMS API",
        default_version="v1",
        description="API documentation for the LMS backend",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# ✅ Health check view
def health_check(request):
    return JsonResponse({"status": "ok"}, status=200)

# ✅ URL patterns
urlpatterns = [
    # Registration endpoints
    path("register/", RegisterView.as_view(), name="register"),
    path("signup/", SignupView.as_view(), name="signup"),

    # JWT authentication endpoints
    path("login/", CustomTokenObtainPairView.as_view(), name="custom_token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="custom_token_refresh"),

    # Aliases for compatibility
    path("auth/login/", CustomTokenObtainPairView.as_view(), name="auth_login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="auth_refresh"),
    path("api/auth/login/", CustomTokenObtainPairView.as_view(), name="api_auth_login"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="api_auth_refresh"),

    # ✅ Forgot password (reset flow using custom API views)
    path("password-reset/", ForgotPasswordView.as_view(), name="password_reset"),
    path("password-reset-confirm/<uidb64>/<token>/", ResetPasswordConfirmView.as_view(), name="password_reset_confirm"),

    # Router endpoints
    path("", include(router.urls)),

    # API docs
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),

    # Health check
    path("health/", health_check, name="health_check"),
]
