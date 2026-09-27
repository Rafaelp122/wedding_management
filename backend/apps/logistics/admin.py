# backend/apps/logistics/admin.py
from django.contrib import admin

from .models import Item


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = [
        "name",
        "wedding",
        "contract",
        "quantity",
        "acquisition_status",
    ]
    list_filter = ["acquisition_status", "wedding"]
    search_fields = [
        "name",
        "description",
        "wedding__groom_name",
        "wedding__bride_name",
    ]
    readonly_fields = ["created_at", "updated_at"]
