from rest_framework.routers import DefaultRouter
from core.views import EnrollmentViewSet

router = DefaultRouter()
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')

urlpatterns = router.urls
