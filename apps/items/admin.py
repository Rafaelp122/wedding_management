from django.contrib import admin

from .models import Item


# Configuração do modelo Item no painel administrativo do Django
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "category",
        "status",
        "quantity",
        "unit_price",
        "total_cost_display",
        "supplier",
        "wedding",
    )
    search_fields = ("name", "description", "supplier")
    list_filter = ("category", "status", "wedding")
    readonly_fields = ("total_cost_display", "created_at", "updated_at")
    list_per_page = 25
    date_hierarchy = "created_at"

    def total_cost_display(self, obj):
        """Exibe o custo total formatado."""
        return f"R$ {obj.total_cost:,.2f}"

    total_cost_display.short_description = "Custo Total"
    total_cost_display.admin_order_field = "unit_price"
