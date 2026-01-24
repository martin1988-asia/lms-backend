from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/courses/', include('courses.urls')),
    path('api/assignments/', include('assignments.urls')),
    path('api/grades/', include('grades.urls')),
]
