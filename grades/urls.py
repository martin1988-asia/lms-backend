from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GradeViewSet, SubmissionViewSet

# Central DRF router for grades and submissions
router = DefaultRouter()
router.register(r"grades", GradeViewSet, basename="grade")
router.register(r"submissions", SubmissionViewSet, basename="submission")

urlpatterns = [
    # Default router endpoints
    path("", include(router.urls)),

    # ✅ Aliases under /api/ for compatibility with tests and external clients
    path("api/", include(router.urls)),
]
