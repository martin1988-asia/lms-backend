from django.contrib import admin
from .models import StudentProfile, InstructorProfile


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "enrollment_date", "grade_level")
    search_fields = ("user__username", "user__email")


@admin.register(InstructorProfile)
class InstructorProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "hire_date", "expertise")
    search_fields = ("user__username", "user__email")
