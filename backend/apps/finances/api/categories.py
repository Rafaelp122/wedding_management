from django.db.models import QuerySet
from ninja import Router
from ninja.pagination import paginate
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.finances.models.budget_category import BudgetCategory
from apps.finances.schemas import (
    BudgetCategoryIn,
    BudgetCategoryOut,
    BudgetCategoryPatchIn,
)
from apps.finances.services.budget_category_service import BudgetCategoryService
from apps.users.types import AuthRequest


budget_categories_router = Router(tags=["Finances"])


@budget_categories_router.get(
    "/", response=list[BudgetCategoryOut], operation_id="finances_categories_list"
)
@paginate
def list_categories(
    request: AuthRequest, wedding_id: UUID4 | None = None
) -> QuerySet[BudgetCategory]:
    """
    Exibe todos os módulos separadores de custos, como Buffet e Cerimonial.

    ``wedding_id`` é repassado ao service que detém a regra de filtragem;
    esta rota não conhece a lógica de tenancy.
    """
    return BudgetCategoryService.list(request.user.company, wedding_id=wedding_id)


@budget_categories_router.get(
    "/{uuid}/",
    response={200: BudgetCategoryOut, **READ_ERROR_RESPONSES},
    operation_id="finances_categories_read",
)
def get_category(request: AuthRequest, uuid: UUID4) -> BudgetCategory:
    """
    Acessa os detalhamentos da categoria isolada de forma simples e visual.
    Garante a segurança contábil sem vazar detalhes restritos a terceiros.
    """
    return BudgetCategoryService.get(request.user.company, uuid)


@budget_categories_router.post(
    "/",
    response={201: BudgetCategoryOut, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_categories_create",
)
def create_category(
    request: AuthRequest, payload: BudgetCategoryIn
) -> tuple[int, BudgetCategory]:
    """
    Abre mais um bloco de centro de custo em conta específica da festa.
    Associa devidamente ao orçamento atrelado em tela.
    """
    return 201, BudgetCategoryService.create(request.user.company, payload.dict())


@budget_categories_router.patch(
    "/{uuid}/",
    response={200: BudgetCategoryOut, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_categories_update",
)
def update_category(
    request: AuthRequest, uuid: UUID4, payload: BudgetCategoryPatchIn
) -> BudgetCategory:
    """
    Corrige o título, ou altera o valor dos gastos planejados.
    Evita sobrescrições acidentais errôneas em outras rotas.
    """
    instance = BudgetCategoryService.get(request.user.company, uuid)
    return BudgetCategoryService.update(
        request.user.company, instance, payload.dict(exclude_unset=True)
    )


@budget_categories_router.delete(
    "/{uuid}/",
    response={204: None, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_categories_delete",
)
def delete_category(request: AuthRequest, uuid: UUID4) -> tuple[int, None]:
    """
    Fecha um agrupamento no orçamento permanentemente.
    Exclui anotações de faturas de modo destrutivo para balanceamento.
    """
    instance = BudgetCategoryService.get(request.user.company, uuid)
    BudgetCategoryService.delete(request.user.company, instance)
    return 204, None
