from django.contrib import admin

from .models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "phone",
        "email",
        "city",
        "state",
        "rating",
        "is_active",
        "created_at",
    ]
    list_filter = ["is_active", "state", "rating", "created_at"]
    search_fields = ["name", "cnpj", "email", "phone", "city"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        ("Informações Básicas", {"fields": ("name", "cnpj", "is_active")}),
        ("Contato", {"fields": ("phone", "email", "website")}),
        ("Endereço", {"fields": ("address", "city", "state")}),
        ("Avaliação", {"fields": ("rating", "notes")}),
        (
            "Metadata",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
