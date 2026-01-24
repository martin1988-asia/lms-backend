from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EnrollmentViewSet

# Central DRF router for enrollments
router = DefaultRouter()
router.include_format_suffixes = False  # ✅ disable suffix patterns for cleaner URLs
router.register(r"enrollments", EnrollmentViewSet, basename="enrollment")

urlpatterns = [
    path("", include(router.urls)),
]
