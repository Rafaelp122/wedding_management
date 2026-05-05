from django.db.models import QuerySet
from ninja import Router
from ninja.pagination import paginate
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.finances.models.budget import Budget
from apps.finances.schemas import BudgetOut, BudgetPatchIn
from apps.finances.services.budget_service import BudgetService
from apps.users.types import AuthRequest


budgets_router = Router(tags=["Finances"])


@budgets_router.get("/", response=list[BudgetOut], operation_id="finances_budgets_list")
@paginate
def list_budgets(request: AuthRequest) -> QuerySet[Budget]:
    """
    Lista as estatísticas de orçamento geral de todos os casamentos.
    """
    return BudgetService.list(request.user.company)


@budgets_router.get(
    "/{uuid}/",
    response={200: BudgetOut, **READ_ERROR_RESPONSES},
    operation_id="finances_budgets_read",
)
def get_budget(request: AuthRequest, uuid: UUID4) -> Budget:
    """
    Retorna os totais e os saldos remanescentes autorizados de um projeto macro.
    """
    return BudgetService.get(request.user.company, uuid)


@budgets_router.get(
    "/for-wedding/{wedding_uuid}/",
    response={200: BudgetOut, **READ_ERROR_RESPONSES},
    operation_id="finances_budgets_for_wedding",
)
def get_budget_for_wedding(request: AuthRequest, wedding_uuid: UUID4) -> Budget:
    """
    Retorna o orçamento de um casamento específico (lazy-create).
    """
    return BudgetService.get_or_create_for_wedding(request.user.company, wedding_uuid)


@budgets_router.patch(
    "/{uuid}/",
    response={200: BudgetOut, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_budgets_update",
)
def update_budget(request: AuthRequest, uuid: UUID4, payload: BudgetPatchIn) -> Budget:
    """
    Atualiza métricas mestres de gasto e painéis globais.
    Contorna referências numéricas totais.
    """
    instance = BudgetService.get(request.user.company, uuid)
    return BudgetService.update(
        request.user.company, instance, payload.dict(exclude_unset=True)
    )
