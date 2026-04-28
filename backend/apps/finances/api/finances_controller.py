from typing import Any

from django.db.models import QuerySet
from ninja.pagination import paginate
from ninja_extra import (
    ControllerBase,
    api_controller,
    http_delete,
    http_get,
    http_patch,
    http_post,
)
from ninja_extra.permissions import IsAuthenticated
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.finances.dependencies import (
    get_budget,
    get_budget_category,
    get_expense,
    get_installment,
)
from apps.finances.models import Budget, BudgetCategory, Expense, Installment
from apps.finances.schemas import (
    BudgetCategoryIn,
    BudgetCategoryOut,
    BudgetCategoryPatchIn,
    BudgetIn,
    BudgetOut,
    BudgetPatchIn,
    ExpenseIn,
    ExpenseOut,
    ExpensePatchIn,
    InstallmentIn,
    InstallmentOut,
    InstallmentPatchIn,
)
from apps.finances.services.budget_category_service import BudgetCategoryService
from apps.finances.services.budget_service import BudgetService
from apps.finances.services.expense_service import ExpenseService
from apps.finances.services.installment_service import InstallmentService


@api_controller("/finances", tags=["Finances"], permissions=[IsAuthenticated])
class FinanceController(ControllerBase):
    context: Any

    # --- BUDGETS ---

    @http_get(
        "/budgets/", response=list[BudgetOut], operation_id="finances_budgets_list"
    )
    @paginate
    def list_budgets(self) -> QuerySet[Budget]:
        return BudgetService.list(self.context.request.user)

    @http_get(
        "/budgets/{budget_uuid}/",
        response={200: BudgetOut, **READ_ERROR_RESPONSES},
        operation_id="finances_budgets_read",
    )
    def get_budget(self, budget_uuid: UUID4):
        return get_budget(self.context.request, budget_uuid)

    @http_get(
        "/budgets/for-wedding/{wedding_uuid}/",
        response={200: BudgetOut, **READ_ERROR_RESPONSES},
        operation_id="finances_budgets_for_wedding",
    )
    def get_budget_for_wedding(self, wedding_uuid: UUID4):
        return BudgetService.get_or_create_for_wedding(
            self.context.request.user, wedding_uuid
        )

    @http_post(
        "/budgets/",
        response={201: BudgetOut, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_budgets_create",
    )
    def create_budget(self, payload: BudgetIn):
        return 201, BudgetService.create(
            self.context.request.user, payload.model_dump()
        )

    @http_patch(
        "/budgets/{budget_uuid}/",
        response={200: BudgetOut, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_budgets_update",
    )
    def update_budget(self, budget_uuid: UUID4, payload: BudgetPatchIn):
        instance = get_budget(self.context.request, budget_uuid)
        return BudgetService.update(instance, payload.model_dump(exclude_unset=True))

    @http_delete(
        "/budgets/{budget_uuid}/",
        response={204: None, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_budgets_delete",
    )
    def delete_budget(self, budget_uuid: UUID4):
        instance = get_budget(self.context.request, budget_uuid)
        BudgetService.delete(instance)
        return 204, None

    # --- CATEGORIES ---

    @http_get(
        "/categories/",
        response=list[BudgetCategoryOut],
        operation_id="finances_categories_list",
    )
    @paginate
    def list_categories(
        self, wedding_id: UUID4 | None = None
    ) -> QuerySet[BudgetCategory]:
        return BudgetCategoryService.list(
            self.context.request.user, wedding_id=wedding_id
        )

    @http_get(
        "/categories/{category_uuid}/",
        response={200: BudgetCategoryOut, **READ_ERROR_RESPONSES},
        operation_id="finances_categories_read",
    )
    def get_category(self, category_uuid: UUID4):
        return get_budget_category(self.context.request, category_uuid)

    @http_post(
        "/categories/",
        response={201: BudgetCategoryOut, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_categories_create",
    )
    def create_category(self, payload: BudgetCategoryIn):
        return 201, BudgetCategoryService.create(
            self.context.request.user, payload.model_dump()
        )

    @http_patch(
        "/categories/{category_uuid}/",
        response={200: BudgetCategoryOut, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_categories_update",
    )
    def update_category(self, category_uuid: UUID4, payload: BudgetCategoryPatchIn):
        instance = get_budget_category(self.context.request, category_uuid)
        return BudgetCategoryService.update(
            instance, payload.model_dump(exclude_unset=True)
        )

    @http_delete(
        "/categories/{category_uuid}/",
        response={204: None, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_categories_delete",
    )
    def delete_category(self, category_uuid: UUID4):
        instance = get_budget_category(self.context.request, category_uuid)
        BudgetCategoryService.delete(instance)
        return 204, None

    # --- EXPENSES ---

    @http_get(
        "/expenses/", response=list[ExpenseOut], operation_id="finances_expenses_list"
    )
    @paginate
    def list_expenses(self, wedding_id: UUID4 | None = None) -> QuerySet[Expense]:
        return ExpenseService.list(self.context.request.user, wedding_id=wedding_id)

    @http_get(
        "/expenses/{expense_uuid}/",
        response={200: ExpenseOut, **READ_ERROR_RESPONSES},
        operation_id="finances_expenses_read",
    )
    def get_expense(self, expense_uuid: UUID4):
        return get_expense(self.context.request, expense_uuid)

    @http_post(
        "/expenses/",
        response={201: ExpenseOut, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_expenses_create",
    )
    def create_expense(self, payload: ExpenseIn):
        return 201, ExpenseService.create(
            self.context.request.user, payload.model_dump()
        )

    @http_patch(
        "/expenses/{expense_uuid}/",
        response={200: ExpenseOut, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_expenses_update",
    )
    def update_expense(self, expense_uuid: UUID4, payload: ExpensePatchIn):
        instance = get_expense(self.context.request, expense_uuid)
        return ExpenseService.update(
            self.context.request.user, instance, payload.model_dump(exclude_unset=True)
        )

    @http_delete(
        "/expenses/{expense_uuid}/",
        response={204: None, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_expenses_delete",
    )
    def delete_expense(self, expense_uuid: UUID4):
        instance = get_expense(self.context.request, expense_uuid)
        ExpenseService.delete(instance)
        return 204, None

    # --- INSTALLMENTS ---

    @http_get(
        "/installments/",
        response=list[InstallmentOut],
        operation_id="finances_installments_list",
    )
    @paginate
    def list_installments(self) -> QuerySet[Installment]:
        return InstallmentService.list(self.context.request.user)

    @http_get(
        "/installments/{installment_uuid}/",
        response={200: InstallmentOut, **READ_ERROR_RESPONSES},
        operation_id="finances_installments_read",
    )
    def get_installment(self, installment_uuid: UUID4):
        return get_installment(self.context.request, installment_uuid)

    @http_post(
        "/installments/",
        response={201: InstallmentOut, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_installments_create",
    )
    def create_installment(self, payload: InstallmentIn):
        return 201, InstallmentService.create(
            self.context.request.user, payload.model_dump()
        )

    @http_patch(
        "/installments/{installment_uuid}/",
        response={200: InstallmentOut, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_installments_update",
    )
    def update_installment(self, installment_uuid: UUID4, payload: InstallmentPatchIn):
        instance = get_installment(self.context.request, installment_uuid)
        return InstallmentService.update(
            instance, payload.model_dump(exclude_unset=True)
        )

    @http_delete(
        "/installments/{installment_uuid}/",
        response={204: None, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_installments_delete",
    )
    def delete_installment(self, installment_uuid: UUID4):
        instance = get_installment(self.context.request, installment_uuid)
        InstallmentService.delete(instance)
        return 204, None
