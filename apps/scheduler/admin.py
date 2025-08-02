from django.contrib import admin
from .models import Schedule


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "datetime", "type", "status", "wedding")
    search_fields = ("title", "description")
    list_filter = ("type", "status", "wedding")
