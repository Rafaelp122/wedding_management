from django.contrib import admin
from .models import Budget


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "wedding",
        "initial_estimate",
        "final_value",
        "status",
        "planner",
    )
    list_filter = ("status", "planner")
    search_fields = (
        "wedding__groom_name",
        "wedding__bride_name",
        "wedding__client__name",
    )
    readonly_fields = ("created_at",)
    list_per_page = 20
