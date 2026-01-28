from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AssignmentViewSet, SubmissionViewSet

# Create DRF router
router = DefaultRouter()

# Register endpoints
router.register(r"assignments", AssignmentViewSet, basename="assignment")
router.register(r"submissions", SubmissionViewSet, basename="submission")

# Expose urlpatterns
urlpatterns = [
    # Default router endpoints
    path("", include(router.urls)),

    # ✅ Aliases under api/ for compatibility with tests
    path("api/", include(router.urls)),
]
