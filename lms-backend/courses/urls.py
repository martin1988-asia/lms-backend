from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, EnrollmentViewSet

# Create DRF router
router = DefaultRouter()
router.include_format_suffixes = False  # disable suffix patterns

# Register endpoints
router.register(r"courses", CourseViewSet, basename="course")
router.register(r"enrollments", EnrollmentViewSet, basename="enrollment")

# Expose urlpatterns
urlpatterns = [
    # Default router endpoints
    path("", include(router.urls)),

    # ✅ Aliases under api/ for compatibility with tests
    path("api/", include(router.urls)),
]
