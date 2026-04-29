# backend/apps/logistics/admin.py
from django.contrib import admin

from .models import Contract, Item, Supplier


class ItemInline(admin.TabularInline):
    model = Item
    extra = 0
    fields = ["name", "quantity", "acquisition_status"]
    show_change_link = True


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ["name", "phone", "email", "is_active"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "email"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "event",
        "supplier",
        "quantity",
        "acquisition_status",
    ]
    list_filter = ["acquisition_status", "event"]
    search_fields = [
        "name",
        "description",
        "event__groom_name",
        "event__bride_name",
    ]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = [
        "event",
        "supplier",
        "budget_category",
        "status",
        "total_amount",
        "signed_date",
    ]
    list_filter = ["status", "expiration_date", "event"]
    search_fields = ["event__groom_name", "event__bride_name", "supplier__name"]
    readonly_fields = [
        "uuid",
        "created_at",
        "updated_at",
    ]
    inlines = [ItemInline]
