from django.contrib import admin
from .models import Grade


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("submission", "instructor", "score", "letter", "graded_at")
    search_fields = ("submission__assignment__title", "submission__student__username", "instructor__username")
    list_filter = ("letter", "graded_at")
