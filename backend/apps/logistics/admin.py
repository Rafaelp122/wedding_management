# backend/apps/logistics/admin.py
from django.contrib import admin

from .models import Contract, Item, Supplier


class ItemInline(admin.TabularInline):  # type: ignore[type-arg]
    model = Item
    extra = 0
    fields = ["name", "quantity", "acquisition_status"]
    show_change_link = True


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ["name", "phone", "email", "is_active"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "email"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = [
        "name",
        "wedding",
        "supplier",
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


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = [
        "wedding",
        "supplier",
        "status",
        "total_amount",
        "signed_date",
    ]
    list_filter = ["status", "expiration_date", "wedding"]
    search_fields = ["wedding__groom_name", "wedding__bride_name", "supplier__name"]
    readonly_fields = [
        "uuid",
        "created_at",
        "updated_at",
    ]
    inlines = [ItemInline]
