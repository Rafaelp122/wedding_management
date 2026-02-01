from django.contrib import admin

from .models import Budget, BudgetCategory, Wedding


class BudgetCategoryInline(admin.TabularInline):
    model = BudgetCategory
    extra = 1
    fields = ["name", "allocated_budget", "description"]
    show_change_link = True


class BudgetInline(admin.StackedInline):
    model = Budget
    extra = 0
    fields = [
        "total_estimated",
        "notes",
        "total_spent",
        "total_paid",
        "total_pending",
        "financial_health",
        "remaining_budget",
    ]
    readonly_fields = [
        "total_spent",
        "total_paid",
        "total_pending",
        "financial_health",
        "remaining_budget",
    ]
    can_delete = False


@admin.register(Wedding)
class WeddingAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "groom_name",
        "bride_name",
        "date",
        "location",
        "status",
        "planner",
    ]
    list_filter = ["status", "date", "planner"]
    search_fields = ["groom_name", "bride_name", "location"]
    date_hierarchy = "date"
    readonly_fields = ["created_at", "updated_at"]
    inlines = [BudgetInline]

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


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = [
        "wedding",
        "total_estimated",
        "total_spent",
        "financial_health_display",
        "created_at",
    ]
    list_filter = ["created_at"]
    search_fields = ["wedding__groom_name", "wedding__bride_name"]
    readonly_fields = [
        "total_spent",
        "total_paid",
        "total_pending",
        "total_overdue",
        "financial_health",
        "remaining_budget",
        "created_at",
        "updated_at",
    ]
    inlines = [BudgetCategoryInline]

    fieldsets = [
        (
            "Informações Básicas",
            {
                "fields": ["wedding", "total_estimated", "notes"],
            },
        ),
        (
            "Resumo Financeiro (RF05)",
            {
                "fields": [
                    "total_spent",
                    "total_paid",
                    "total_pending",
                    "total_overdue",
                    "financial_health",
                    "remaining_budget",
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

    def financial_health_display(self, obj):
        return f"{obj.financial_health:.2f}%"

    financial_health_display.short_description = "Saúde Financeira"


@admin.register(BudgetCategory)
class BudgetCategoryAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "budget",
        "allocated_budget",
        "total_spent",
        "remaining_budget",
    ]
    list_filter = ["budget__wedding"]
    search_fields = [
        "name",
        "budget__wedding__groom_name",
        "budget__wedding__bride_name",
    ]
    readonly_fields = ["total_spent", "remaining_budget", "created_at", "updated_at"]

    fieldsets = [
        (
            "Informações da Categoria",
            {
                "fields": ["budget", "name", "description", "allocated_budget"],
            },
        ),
        (
            "Resumo Financeiro",
            {
                "fields": ["total_spent", "remaining_budget"],
            },
        ),
        (
            "Metadados",
            {
                "fields": ["created_at", "updated_at"],
            },
        ),
    ]
