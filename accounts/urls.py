from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    SignupView,
    ProfileViewSet,
    CustomUserViewSet,
    CustomTokenObtainPairView,
    ForgotPasswordView,
    ResetPasswordConfirmView,
)
from django.http import JsonResponse

# ✅ Router setup
router = DefaultRouter()
router.register(r"profile", ProfileViewSet, basename="profile")
router.register(r"users", CustomUserViewSet, basename="user")

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

    # Aliases for compatibility (global wiring under /api/auth/)
    path("auth/login/", CustomTokenObtainPairView.as_view(), name="auth_login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="auth_refresh"),
    path("api/auth/login/", CustomTokenObtainPairView.as_view(), name="api_auth_login"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="api_auth_refresh"),

    # ✅ Forgot password (reset flow using custom API views)
    path("password-reset/", ForgotPasswordView.as_view(), name="password_reset"),
    path("password-reset-confirm/<uidb64>/<token>/", ResetPasswordConfirmView.as_view(), name="password_reset_confirm"),

    # Router endpoints (includes /users/me/ automatically via CustomUserViewSet)
    path("", include(router.urls)),

    # Health check (namespaced under accounts)
    path("health/", health_check, name="health_check"),
]
