from django.contrib import admin

from .models import Wedding


@admin.register(Wedding)
class WeddingAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "groom_name",
        "bride_name",
        "date",
        "location",
        "expected_guests",
        "status",
        "planner",
    ]
    list_filter = ["status", "date", "planner"]
    search_fields = ["groom_name", "bride_name", "location"]
    date_hierarchy = "date"
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = [
        (
            "Informações do Casamento",
            {
                "fields": [
                    "planner",
                    "groom_name",
                    "bride_name",
                    "date",
                    "location",
                    "status",
                ],
            },
        ),
        (
            "Metadados",
            {
                "fields": ["created_at", "updated_at"],
            },
        ),
    ]
