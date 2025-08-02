from django.contrib import admin
from .models import Contract


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ("id", "wedding", "created_at", "status")
    search_fields = ("wedding__client__name",)
    list_filter = ("status", "wedding")
