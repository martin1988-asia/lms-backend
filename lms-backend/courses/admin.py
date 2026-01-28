from django.contrib import admin
from .models import Course, Enrollment


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "instructor", "created_at")
    search_fields = ("title", "description", "instructor__username")
    list_filter = ("created_at",)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "date_enrolled")
    search_fields = ("student__username", "course__title")
    list_filter = ("date_enrolled",)
