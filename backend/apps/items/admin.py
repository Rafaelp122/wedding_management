from django.contrib import admin

from .models import Installment, Item


class InstallmentInline(admin.TabularInline):
    model = Installment
    extra = 1
    fields = [
        "installment_number",
        "amount",
        "due_date",
        "paid_date",
        "status",
        "notes",
    ]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "wedding",
        "budget_category",
        "acquisition_status",
        "quantity",
        "estimated_cost",
        "actual_cost",
        "total_cost_display",
        "get_supplier_name",
    )
    search_fields = ("name", "description", "supplier__name")
    list_filter = ("budget_category", "acquisition_status", "wedding")
    readonly_fields = (
        "total_cost_display",
        "total_paid",
        "total_pending",
        "balance",
        "created_at",
        "updated_at",
    )
    list_per_page = 25
    date_hierarchy = "created_at"
    inlines = [InstallmentInline]

    @admin.display(description="Fornecedor", ordering="supplier__name")
    def get_supplier_name(self, obj):
        return obj.supplier.name if obj.supplier else "-"

    fieldsets = [
        (
            "Informações Básicas",
            {
                "fields": ["wedding", "name", "description", "budget_category"],
            },
        ),
        (
            "Logística (RF06/RF07)",
            {
                "fields": ["supplier", "quantity", "acquisition_status"],
            },
        ),
        (
            "Financeiro (RF03/RF04)",
            {
                "fields": [
                    "estimated_cost",
                    "actual_cost",
                    "total_cost_display",
                    "total_paid",
                    "total_pending",
                    "balance",
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

    def total_cost_display(self, obj):
        """Exibe o custo total formatado."""
        return f"R$ {obj.total_cost:,.2f}"

    total_cost_display.short_description = "Custo Total"
    total_cost_display.admin_order_field = "actual_cost"


@admin.register(Installment)
class InstallmentAdmin(admin.ModelAdmin):
    list_display = [
        "item",
        "installment_number",
        "amount",
        "due_date",
        "paid_date",
        "status",
    ]
    list_filter = ["status", "due_date", "item__wedding"]
    search_fields = ["item__name"]
    date_hierarchy = "due_date"
    readonly_fields = ["created_at", "updated_at"]
