from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    CourseViewSet,
    ModuleViewSet,
    AssignmentViewSet,
    SubmissionViewSet,
    RegisterUserView,  # ✅ import registration view
)

# Create a router and register our viewsets
router = DefaultRouter()
router.include_format_suffixes = False  # disable suffix patterns

router.register(r"users", UserViewSet, basename="user")
router.register(r"courses", CourseViewSet, basename="course")
router.register(r"modules", ModuleViewSet, basename="module")
router.register(r"assignments", AssignmentViewSet, basename="assignment")
router.register(r"submissions", SubmissionViewSet, basename="submission")

# Expose urlpatterns
urlpatterns = [
    # ✅ Registration endpoint for users app
    path("register/", RegisterUserView.as_view(), name="user-register"),

    # ✅ Router-generated endpoints
    path("", include(router.urls)),
]
