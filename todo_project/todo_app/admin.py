from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "done", "created_at", "completed_at")
    list_filter = ("done",)
    search_fields = ("title", "description")
