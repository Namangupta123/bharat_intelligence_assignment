from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_by', 'assigned_manager', 'created_at')
    list_filter = ('status',)
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')
