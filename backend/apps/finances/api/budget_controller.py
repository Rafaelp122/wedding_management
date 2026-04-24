from django.db.models import QuerySet
from ninja.pagination import paginate
from ninja_extra import (
    ControllerBase,
    api_controller,
    http_get,
    http_patch,
)
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.finances.models import Budget
from apps.finances.schemas import BudgetOut, BudgetPatchIn
from apps.finances.services import BudgetService


@api_controller("/finances/budgets", tags=["Finances"])
class BudgetController(ControllerBase):
    def __init__(self, service: BudgetService):
        self.service = service

    @http_get("/", response=list[BudgetOut], operation_id="finances_budgets_list")
    @paginate
    def list_budgets(self) -> QuerySet[Budget]:
        """Lista estatísticas de orçamento de todos os casamentos."""
        return self.service.list(self.context.request.user)

    @http_get(
        "/{wedding_id}/",
        response={200: BudgetOut, **READ_ERROR_RESPONSES},
        operation_id="finances_budgets_read",
    )
    def retrieve_budget(self, wedding_id: UUID4) -> Budget:
        """Retorna o orçamento mestre de um casamento."""
        return self.service.get_or_create_for_wedding(
            self.context.request.user, wedding_id
        )

    @http_patch(
        "/{wedding_id}/",
        response={200: BudgetOut, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_budgets_partial_update",
    )
    def update_budget(self, wedding_id: UUID4, payload: BudgetPatchIn) -> Budget:
        """Atualiza o teto orçamentário."""
        return self.service.update_by_wedding(
            self.context.request.user,
            wedding_id,
            payload.model_dump(exclude_unset=True),
        )
