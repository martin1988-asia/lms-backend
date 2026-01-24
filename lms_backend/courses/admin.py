from django.contrib import admin
from .models import Course
from assignments.models import Assignment

class AssignmentInline(admin.TabularInline):
    model = Assignment
    extra = 1  # show one empty row for quick adding

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description')
    search_fields = ('title', 'description')
    inlines = [AssignmentInline]
