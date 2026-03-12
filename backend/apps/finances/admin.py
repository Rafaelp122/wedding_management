# backend/apps/finances/admin.py
from django.contrib import admin

from .models import Budget, BudgetCategory, Expense, Installment


class BudgetCategoryInline(admin.TabularInline):
    model = BudgetCategory
    extra = 1
    fields = ["name", "allocated_budget", "description"]
    show_change_link = True


class ExpenseInline(admin.TabularInline):
    # AJUSTE: Removido estimated_amount se ele não existir mais no model
    model = Expense
    extra = 0
    fields = ["description", "actual_amount", "contract"]
    show_change_link = True


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    # AJUSTE: search_fields corrigido para o novo modelo de Wedding
    list_display = ["wedding", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["wedding__groom_name", "wedding__bride_name"]
    readonly_fields = ["uuid", "created_at", "updated_at"]
    inlines = [BudgetCategoryInline]

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(BudgetCategory)
class BudgetCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "budget", "allocated_budget"]
    list_filter = ["budget", "created_at"]
    # AJUSTE: search_fields corrigido
    search_fields = [
        "name",
        "budget__wedding__groom_name",
        "budget__wedding__bride_name",
    ]
    readonly_fields = ["uuid", "created_at", "updated_at"]
    inlines = [ExpenseInline]

    def has_delete_permission(self, request, obj=None):
        return False


class InstallmentInline(admin.TabularInline):
    model = Installment
    extra = 1
    fields = ["installment_number", "due_date", "amount", "paid_date", "status"]


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = [
        "description",
        "category",
        "actual_amount",
        "contract",
        "created_at",
    ]
    list_filter = ["category__budget", "created_at"]
    search_fields = [
        "description",
        "category__name",
        "wedding__groom_name",
        "wedding__bride_name",
    ]
    readonly_fields = ["uuid", "created_at", "updated_at"]
    inlines = [InstallmentInline]

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Installment)
class InstallmentAdmin(admin.ModelAdmin):
    list_display = ["expense", "installment_number", "due_date", "amount", "status"]
    list_filter = ["status", "due_date"]
    search_fields = ["expense__description"]
    readonly_fields = ["uuid", "created_at", "updated_at"]

    def has_delete_permission(self, request, obj=None):
        return False
