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
from apps.finances.dependencies import get_expense
from apps.finances.models import Expense
from apps.finances.schemas import ExpenseIn, ExpenseOut, ExpensePatchIn
from apps.finances.services.expense_service import ExpenseService


@api_controller("/finances/expenses", tags=["Finances"])
class ExpenseController(ControllerBase):
    @http_get("/", response=list[ExpenseOut], operation_id="finances_expenses_list")
    @paginate
    def list_expenses(self, event_id: UUID4 | None = None) -> QuerySet[Expense]:
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        assert self.context.request.user  # noqa: S101
        return ExpenseService.list(self.context.request.user, event_id=event_id)

    @http_get(
        "/{expense_uuid}/",
        response={200: ExpenseOut, **READ_ERROR_RESPONSES},
        operation_id="finances_expenses_read",
    )
    def get_expense(self, expense_uuid: UUID4):
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        return get_expense(self.context.request, expense_uuid)

    @http_post(
        "/",
        response={201: ExpenseOut, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_expenses_create",
    )
    def create_expense(self, payload: ExpenseIn):
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        assert self.context.request.user  # noqa: S101
        return 201, ExpenseService.create(
            self.context.request.user, payload.model_dump()
        )

    @http_patch(
        "/{expense_uuid}/",
        response={200: ExpenseOut, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_expenses_update",
    )
    def update_expense(self, expense_uuid: UUID4, payload: ExpensePatchIn):
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        assert self.context.request.user  # noqa: S101
        instance = get_expense(self.context.request, expense_uuid)
        return ExpenseService.update(
            self.context.request.user, instance, payload.model_dump(exclude_unset=True)
        )

    @http_delete(
        "/{expense_uuid}/",
        response={204: None, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_expenses_delete",
    )
    def delete_expense(self, expense_uuid: UUID4):
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        instance = get_expense(self.context.request, expense_uuid)
        ExpenseService.delete(instance)
        return 204, None
