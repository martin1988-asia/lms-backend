from django.contrib import admin
from .models import Grade

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('id', 'assignment', 'score', 'feedback')
    search_fields = ('feedback',)
    list_filter = ('assignment', 'score')
