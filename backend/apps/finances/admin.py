from django.contrib import admin

from .models import Budget, BudgetCategory, Expense, Installment


class BudgetCategoryInline(admin.TabularInline):
    model = BudgetCategory
    extra = 1
    fields = ["name", "allocated_budget", "description"]
    show_change_link = True


class ExpenseInline(admin.TabularInline):
    model = Expense
    extra = 0
    fields = ["description", "estimated_amount", "actual_amount", "contract"]
    show_change_link = True


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ["wedding", "total_estimated", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["wedding__groom_name", "wedding__bride_name"]
    readonly_fields = ["created_at", "updated_at"]
    inlines = [BudgetCategoryInline]


@admin.register(BudgetCategory)
class BudgetCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "budget", "allocated_budget", "is_deleted"]
    list_filter = ["budget", "is_deleted", "created_at"]
    search_fields = [
        "name",
        "budget__wedding__groom_name",
        "budget__wedding__bride_name",
    ]
    readonly_fields = ["created_at", "updated_at", "deleted_at"]
    inlines = [ExpenseInline]


class InstallmentInline(admin.TabularInline):
    model = Installment
    extra = 1
    fields = ["installment_number", "due_date", "amount", "paid_date", "status"]


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = [
        "description",
        "category",
        "estimated_amount",
        "actual_amount",
        "contract",
        "created_at",
    ]
    list_filter = ["category__budget", "created_at"]
    search_fields = ["description", "category__name"]
    readonly_fields = ["created_at", "updated_at"]
    inlines = [InstallmentInline]

    def has_delete_permission(self, request, obj=None):
        # Bloqueia delete de despesas (integridade financeira)
        return False


@admin.register(Installment)
class InstallmentAdmin(admin.ModelAdmin):
    list_display = ["expense", "installment_number", "due_date", "amount", "status"]
    list_filter = ["status", "due_date"]
    search_fields = ["expense__description"]
    readonly_fields = ["created_at", "updated_at"]

    def has_delete_permission(self, request, obj=None):
        # Bloqueia delete de parcelas (integridade financeira)
        return False
