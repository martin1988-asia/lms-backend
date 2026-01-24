from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AssignmentViewSet, SubmissionViewSet

# Create DRF router
router = DefaultRouter()
router.include_format_suffixes = False  # disable suffix patterns

# Register endpoints
router.register(r"assignments", AssignmentViewSet, basename="assignment")
router.register(r"submissions", SubmissionViewSet, basename="submission")

# Expose urlpatterns
urlpatterns = [
    path("", include(router.urls)),
]
