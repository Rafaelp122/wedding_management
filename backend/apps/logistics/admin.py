# backend/apps/logistics/admin.py
from django.contrib import admin

from .models import Contract, Item, Supplier


class ItemInline(admin.TabularInline):
    model = Item
    extra = 0
    fields = ["name", "quantity", "budget_category", "acquisition_status"]
    show_change_link = True


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ["name", "phone", "email", "is_active", "is_deleted"]
    list_filter = ["is_active", "is_deleted", "created_at"]
    search_fields = ["name", "email"]
    readonly_fields = ["created_at", "updated_at", "deleted_at"]


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "wedding",
        "supplier",
        "budget_category",
        "quantity",
        "acquisition_status",
        "is_deleted",
    ]
    list_filter = ["acquisition_status", "is_deleted", "wedding", "budget_category"]
    search_fields = ["name", "description", "wedding__name"]
    readonly_fields = ["created_at", "updated_at", "deleted_at"]


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = [
        "wedding",
        "supplier",
        "status",  # Adicionado para controle
        "total_amount",  # Adicionado para controle
        "signed_date",  # Adicionado para controle
        "is_deleted",
    ]
    list_filter = ["status", "is_deleted", "expiration_date", "wedding"]
    search_fields = ["wedding__name", "supplier__name"]
    readonly_fields = [
        "uuid",
        "created_at",
        "updated_at",
        "deleted_at",
    ]
    inlines = [ItemInline]
