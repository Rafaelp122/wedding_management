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
from apps.events.models import Event
from apps.finances.dependencies import get_budget
from apps.finances.models import Budget
from apps.finances.schemas import BudgetIn, BudgetOut, BudgetPatchIn
from apps.finances.services.budget_service import BudgetService


@api_controller("/finances/budgets", tags=["Finances"])
class BudgetController(ControllerBase):
    @http_get("/", response=list[BudgetOut], operation_id="finances_budgets_list")
    @paginate
    def list_budgets(self) -> QuerySet[Budget]:
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        assert self.context.request.user  # noqa: S101
        return BudgetService.list(self.context.request.user)

    @http_get(
        "/{budget_uuid}/",
        response={200: BudgetOut, **READ_ERROR_RESPONSES},
        operation_id="finances_budgets_read",
    )
    def get_budget(self, budget_uuid: UUID4):
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        return get_budget(self.context.request, budget_uuid)

    @http_get(
        "/for-event/{event_uuid}/",
        response={200: BudgetOut, **READ_ERROR_RESPONSES},
        operation_id="finances_budgets_for_event",
    )
    def get_budget_for_event(self, event_uuid: UUID4):
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        assert self.context.request.user  # noqa: S101

        # Proteção contra IDOR: Garante que o evento pertence ao usuário
        event = Event.objects.resolve(self.context.request.user, event_uuid)

        return BudgetService.get_or_create_for_event(
            self.context.request.user, event.uuid
        )

    @http_post(
        "/",
        response={201: BudgetOut, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_budgets_create",
    )
    def create_budget(self, payload: BudgetIn):
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        assert self.context.request.user  # noqa: S101
        return 201, BudgetService.create(
            self.context.request.user, payload.model_dump()
        )

    @http_patch(
        "/{budget_uuid}/",
        response={200: BudgetOut, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_budgets_update",
    )
    def update_budget(self, budget_uuid: UUID4, payload: BudgetPatchIn):
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        instance = get_budget(self.context.request, budget_uuid)
        return BudgetService.update(instance, payload.model_dump(exclude_unset=True))

    @http_delete(
        "/{budget_uuid}/",
        response={204: None, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_budgets_delete",
    )
    def delete_budget(self, budget_uuid: UUID4):
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        instance = get_budget(self.context.request, budget_uuid)
        BudgetService.delete(instance)
        return 204, None
