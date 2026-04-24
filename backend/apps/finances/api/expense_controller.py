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
from apps.finances.models import Expense
from apps.finances.schemas import (
    ExpenseIn,
    ExpenseOut,
    ExpensePatchIn,
)
from apps.finances.services import ExpenseService


@api_controller("/finances/expenses", tags=["Finances"])
class ExpenseController(ControllerBase):
    def __init__(self, service: ExpenseService):
        self.service = service

    @http_get("/", response=list[ExpenseOut], operation_id="finances_expenses_list")
    @paginate
    def list_expenses(self, wedding_id: UUID4 | None = None) -> QuerySet[Expense]:
        """Lista todas as despesas."""
        return self.service.list(self.context.request.user, wedding_id=wedding_id)

    @http_get(
        "/{uuid}/",
        response={200: ExpenseOut, **READ_ERROR_RESPONSES},
        operation_id="finances_expenses_read",
    )
    def retrieve_expense(self, uuid: UUID4) -> Expense:
        """Retorna detalhes de uma despesa."""
        return self.service.get(self.context.request.user, uuid=uuid)

    @http_post(
        "/",
        response={201: ExpenseOut, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_expenses_create",
    )
    def create_expense(self, payload: ExpenseIn) -> tuple[int, Expense]:
        """Cria uma nova despesa."""
        expense = self.service.create(self.context.request.user, payload.model_dump())
        return 201, expense

    @http_patch(
        "/{uuid}/",
        response={200: ExpenseOut, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_expenses_partial_update",
    )
    def partial_update_expense(self, uuid: UUID4, payload: ExpensePatchIn) -> Expense:
        """Atualiza parcialmente uma despesa."""
        instance = self.service.get(self.context.request.user, uuid=uuid)
        return self.service.partial_update(
            self.context.request.user, instance, payload.model_dump(exclude_unset=True)
        )

    @http_delete(
        "/{uuid}/",
        response={204: None, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_expenses_delete",
    )
    def delete_expense(self, uuid: UUID4) -> tuple[int, None]:
        """Remove uma despesa."""
        self.service.delete(self.context.request.user, uuid)
        return 204, None
