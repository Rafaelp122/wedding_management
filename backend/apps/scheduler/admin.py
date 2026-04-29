from django.contrib import admin

from .models import Appointment, Task


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "event_type", "start_time", "end_time")
    list_filter = ("event_type", "company", "start_time")
    search_fields = ("title", "description", "location")


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "event_id", "is_completed", "due_date")
    list_filter = ("is_completed", "company", "due_date")
    search_fields = ("title", "description")
