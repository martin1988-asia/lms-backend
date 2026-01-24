from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView,
    SignupView,
    ProfileViewSet,
    CustomUserViewSet,
    CustomTokenObtainPairView,
)

# Create a router and register our viewsets
router = DefaultRouter()
router.include_format_suffixes = False  # disable suffix patterns

# Register endpoints
router.register(r"profile", ProfileViewSet, basename="profile")
router.register(r"users", CustomUserViewSet, basename="user")

# Expose urlpatterns
urlpatterns = [
    # Registration endpoints
    path("register/", RegisterView.as_view(), name="register"),
    path("signup/", SignupView.as_view(), name="signup"),

    # JWT authentication endpoints
    path("login/", CustomTokenObtainPairView.as_view(), name="custom_token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="custom_token_refresh"),

    # Router-generated endpoints (profile-list, user-list, etc.)
    path("", include(router.urls)),
]
