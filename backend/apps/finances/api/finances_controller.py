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
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.finances.models import Budget, BudgetCategory, Expense, Installment
from apps.finances.schemas import (
    BudgetCategoryIn,
    BudgetCategoryOut,
    BudgetCategoryPatchIn,
    BudgetOut,
    BudgetPatchIn,
    ExpenseIn,
    ExpenseOut,
    ExpensePatchIn,
    InstallmentIn,
    InstallmentOut,
    InstallmentPatchIn,
)
from apps.finances.services import (
    BudgetCategoryService,
    BudgetService,
    ExpenseService,
    InstallmentService,
)


@api_controller("/finances", tags=["Finances"])
class FinancesController(ControllerBase):
    """
    Controller para gestão financeira completa.
    Centraliza orçamentos, categorias, despesas e parcelas.
    """

    def __init__(
        self,
        budget_service: BudgetService,
        category_service: BudgetCategoryService,
        expense_service: ExpenseService,
        installment_service: InstallmentService,
    ):
        self.budget_service = budget_service
        self.category_service = category_service
        self.expense_service = expense_service
        self.installment_service = installment_service

    # --- Endpoints de Orçamentos (Budgets) ---

    @http_get(
        "/budgets/", response=list[BudgetOut], operation_id="finances_budgets_list"
    )
    @paginate
    def list_budgets(self) -> QuerySet[Budget]:
        """Lista estatísticas de orçamento de todos os casamentos."""
        return self.budget_service.list(self.context.request.user)

    @http_get(
        "/budgets/{wedding_id}/",
        response={200: BudgetOut, **READ_ERROR_RESPONSES},
        operation_id="finances_budgets_read",
    )
    def retrieve_budget(self, wedding_id: UUID4) -> Budget:
        """Retorna o orçamento mestre de um casamento."""
        return self.budget_service.get_or_create_for_wedding(
            self.context.request.user, wedding_id
        )

    @http_patch(
        "/budgets/{wedding_id}/",
        response={200: BudgetOut, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_budgets_partial_update",
    )
    def update_budget(self, wedding_id: UUID4, payload: BudgetPatchIn) -> Budget:
        """Atualiza o teto orçamentário."""
        return self.budget_service.update_by_wedding(
            self.context.request.user,
            wedding_id,
            payload.model_dump(exclude_unset=True),
        )

    # --- Endpoints de Categorias ---

    @http_get(
        "/categories/",
        response=list[BudgetCategoryOut],
        operation_id="finances_categories_list",
    )
    @paginate
    def list_categories(self) -> QuerySet[BudgetCategory]:
        """Lista categorias de custo."""
        return self.category_service.list(self.context.request.user)

    @http_get(
        "/categories/{uuid}/",
        response={200: BudgetCategoryOut, **READ_ERROR_RESPONSES},
        operation_id="finances_categories_read",
    )
    def retrieve_category(self, uuid: UUID4) -> BudgetCategory:
        """Retorna detalhes de uma categoria."""
        return self.category_service.get(self.context.request.user, uuid=uuid)

    @http_post(
        "/categories/",
        response={201: BudgetCategoryOut, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_categories_create",
    )
    def create_category(self, payload: BudgetCategoryIn) -> tuple[int, BudgetCategory]:
        """Cria uma nova categoria orçamentária."""
        category = self.category_service.create(
            self.context.request.user, payload.model_dump()
        )
        return 201, category

    @http_patch(
        "/categories/{uuid}/",
        response={200: BudgetCategoryOut, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_categories_partial_update",
    )
    def partial_update_category(
        self, uuid: UUID4, payload: BudgetCategoryPatchIn
    ) -> BudgetCategory:
        """Atualiza parcialmente uma categoria."""
        instance = self.category_service.get(self.context.request.user, uuid=uuid)
        return self.category_service.partial_update(
            self.context.request.user, instance, payload.model_dump(exclude_unset=True)
        )

    @http_delete(
        "/categories/{uuid}/",
        response={204: None, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_categories_delete",
    )
    def delete_category(self, uuid: UUID4) -> tuple[int, None]:
        """Remove uma categoria."""
        self.category_service.delete(self.context.request.user, uuid)
        return 204, None

    # --- Endpoints de Despesas (Expenses) ---

    @http_get(
        "/expenses/", response=list[ExpenseOut], operation_id="finances_expenses_list"
    )
    @paginate
    def list_expenses(self, wedding_id: UUID4 | None = None) -> QuerySet[Expense]:
        """Lista todas as despesas."""
        return self.expense_service.list(
            self.context.request.user, wedding_id=wedding_id
        )

    @http_get(
        "/expenses/{uuid}/",
        response={200: ExpenseOut, **READ_ERROR_RESPONSES},
        operation_id="finances_expenses_read",
    )
    def retrieve_expense(self, uuid: UUID4) -> Expense:
        """Retorna detalhes de uma despesa."""
        return self.expense_service.get(self.context.request.user, uuid=uuid)

    @http_post(
        "/expenses/",
        response={201: ExpenseOut, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_expenses_create",
    )
    def create_expense(self, payload: ExpenseIn) -> tuple[int, Expense]:
        """Cria uma nova despesa."""
        expense = self.expense_service.create(
            self.context.request.user, payload.model_dump()
        )
        return 201, expense

    @http_patch(
        "/expenses/{uuid}/",
        response={200: ExpenseOut, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_expenses_partial_update",
    )
    def partial_update_expense(self, uuid: UUID4, payload: ExpensePatchIn) -> Expense:
        """Atualiza parcialmente uma despesa."""
        instance = self.expense_service.get(self.context.request.user, uuid=uuid)
        return self.expense_service.partial_update(
            self.context.request.user, instance, payload.model_dump(exclude_unset=True)
        )

    @http_delete(
        "/expenses/{uuid}/",
        response={204: None, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_expenses_delete",
    )
    def delete_expense(self, uuid: UUID4) -> tuple[int, None]:
        """Remove uma despesa."""
        self.expense_service.delete(self.context.request.user, uuid)
        return 204, None

    # --- Endpoints de Parcelas (Installments) ---

    @http_get(
        "/installments/",
        response=list[InstallmentOut],
        operation_id="finances_installments_list",
    )
    @paginate
    def list_installments(self) -> QuerySet[Installment]:
        """Lista parcelas/pagamentos."""
        return self.installment_service.list(self.context.request.user)

    @http_get(
        "/installments/{uuid}/",
        response={200: InstallmentOut, **READ_ERROR_RESPONSES},
        operation_id="finances_installments_read",
    )
    def retrieve_installment(self, uuid: UUID4) -> Installment:
        """Retorna detalhes de uma parcela."""
        return self.installment_service.get(self.context.request.user, uuid=uuid)

    @http_post(
        "/installments/",
        response={201: InstallmentOut, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_installments_create",
    )
    def create_installment(self, payload: InstallmentIn) -> tuple[int, Installment]:
        """Cria uma nova parcela."""
        installment = self.installment_service.create(
            self.context.request.user, payload.model_dump()
        )
        return 201, installment

    @http_patch(
        "/installments/{uuid}/",
        response={200: InstallmentOut, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_installments_partial_update",
    )
    def partial_update_installment(
        self, uuid: UUID4, payload: InstallmentPatchIn
    ) -> Installment:
        """Atualiza parcialmente uma parcela."""
        instance = self.installment_service.get(self.context.request.user, uuid=uuid)
        return self.installment_service.partial_update(
            self.context.request.user, instance, payload.model_dump(exclude_unset=True)
        )

    @http_delete(
        "/installments/{uuid}/",
        response={204: None, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_installments_delete",
    )
    def delete_installment(self, uuid: UUID4) -> tuple[int, None]:
        """Remove uma parcela."""
        self.installment_service.delete(self.context.request.user, uuid)
        return 204, None
