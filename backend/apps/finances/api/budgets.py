from typing import Any

from django.http import HttpRequest
from ninja import Router
from ninja.pagination import paginate
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.finances.schemas import BudgetIn, BudgetOut, BudgetPatchIn
from apps.finances.services.budget_service import BudgetService


budgets_router = Router(tags=["Finances"])


@budgets_router.get("/", response=list[BudgetOut], operation_id="finances_budgets_list")
@paginate
def list_budgets(request: HttpRequest) -> Any:
    """
    Lista as estatísticas de orçamento geral de todos os casamentos.
    """
    return BudgetService.list(request.user)


@budgets_router.get(
    "/{uuid}/",
    response={200: BudgetOut, **READ_ERROR_RESPONSES},
    operation_id="finances_budgets_read",
)
def get_budget(request: HttpRequest, uuid: UUID4) -> Any:
    """
    Retorna os totais e os saldos remanescentes autorizados de um projeto macro.
    """
    return BudgetService.get(request.user, uuid)


@budgets_router.get(
    "/for-wedding/{wedding_uuid}/",
    response={200: BudgetOut, **READ_ERROR_RESPONSES},
    operation_id="finances_budgets_for_wedding",
)
def get_budget_for_wedding(request: HttpRequest, wedding_uuid: UUID4) -> Any:
    """
    Retorna o orçamento de um casamento específico.

    Implementa o padrão Lazy Loading:
    - Se o Budget já existe, retorna ele
    - Se não existe, cria automaticamente com total_estimated=0 e categorias padrão

    Este endpoint permite que o frontend acesse o orçamento sem se preocupar
    se ele foi criado ou não durante a criação do casamento.
    """
    return BudgetService.get_or_create_for_wedding(request.user, wedding_uuid)


@budgets_router.post(
    "/",
    response={201: BudgetOut, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_budgets_create",
)
def create_budget(request: HttpRequest, payload: BudgetIn) -> Any:
    """
    Dá pontapé inicial para a planilha contábil centralizada.
    Atrelada às métricas cerimoniais.
    """
    return 201, BudgetService.create(request.user, payload.dict())


@budgets_router.patch(
    "/{uuid}/",
    response={200: BudgetOut, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_budgets_partial_update",
)
def partial_update_budget(
    request: HttpRequest, uuid: UUID4, payload: BudgetPatchIn
) -> Any:
    """
    Atualiza métricas mestres de gasto e painéis globais.
    Contorna referências numéricas totais.
    """
    instance = BudgetService.get(request.user, uuid)
    return BudgetService.partial_update(
        request.user, instance, payload.dict(exclude_unset=True)
    )


@budgets_router.delete(
    "/{uuid}/",
    response={204: None, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_budgets_delete",
)
def delete_budget(request: HttpRequest, uuid: UUID4) -> Any:
    """
    Remove toda e qualquer anotação da malha financeira.
    Varre as despesas em ação de reverso total absoluto.
    """
    instance = BudgetService.get(request.user, uuid)
    BudgetService.delete(request.user, instance)
    return 204, None
