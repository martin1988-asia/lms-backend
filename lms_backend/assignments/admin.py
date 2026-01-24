from django.contrib import admin
from .models import Assignment
from grades.models import Grade

class GradeInline(admin.TabularInline):
    model = Grade
    extra = 1

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'title', 'description')
    search_fields = ('title', 'description')
    list_filter = ('course',)
    inlines = [GradeInline]
