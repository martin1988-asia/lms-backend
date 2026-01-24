from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GradeViewSet

# Central DRF router for grades
router = DefaultRouter()
router.include_format_suffixes = False  # ✅ disable suffix patterns for cleaner URLs
router.register(r"grades", GradeViewSet, basename="grade")

urlpatterns = [
    path("", include(router.urls)),
]
