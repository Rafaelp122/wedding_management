from django.contrib import admin

from .models import Wedding, WeddingClient


@admin.register(Wedding)
class WeddingAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = [
        "id",
        "groom_name",
        "bride_name",
        "date",
        "location",
        "expected_guests",
        "status",
        "company",
    ]
    list_filter = ["status", "date", "company"]
    search_fields = ["groom_name", "bride_name", "location"]
    date_hierarchy = "date"
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = [
        (
            "Informações do Casamento",
            {
                "fields": [
                    "company",
                    "groom_name",
                    "bride_name",
                    "date",
                    "location",
                    "expected_guests",
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


@admin.register(WeddingClient)
class WeddingClientAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ["wedding", "client", "role", "is_primary_signatory", "company"]
    list_filter = ["role", "is_primary_signatory", "company"]
    search_fields = ["wedding__groom_name", "wedding__bride_name", "client__name"]
