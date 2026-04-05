from typing import Any

from django.http import HttpRequest
from ninja import Router
from ninja.pagination import paginate
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.finances.schemas import (
    BudgetCategoryIn,
    BudgetCategoryOut,
    BudgetCategoryPatchIn,
)
from apps.finances.services.budget_category_service import BudgetCategoryService


budget_categories_router = Router(tags=["Finances"])


@budget_categories_router.get(
    "/", response=list[BudgetCategoryOut], operation_id="finances_categories_list"
)
@paginate
def list_categories(request: HttpRequest) -> Any:
    """
    Exibe todos os módulos separadores de custos, como Buffet e Cerimonial.
    """
    return BudgetCategoryService.list(request.user)


@budget_categories_router.get(
    "/{uuid}/",
    response={200: BudgetCategoryOut, **READ_ERROR_RESPONSES},
    operation_id="finances_categories_read",
)
def get_category(request: HttpRequest, uuid: UUID4) -> Any:
    """
    Acessa os detalhamentos da categoria isolada de forma simples e visual.
    Garante a segurança contábil sem vazar detalhes restritos a terceiros.
    """
    return BudgetCategoryService.get(request.user, uuid)


@budget_categories_router.post(
    "/",
    response={201: BudgetCategoryOut, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_categories_create",
)
def create_category(request: HttpRequest, payload: BudgetCategoryIn) -> Any:
    """
    Abre mais um bloco de centro de custo em conta específica da festa.
    Associa devidamente ao orçamento atrelado em tela.
    """
    return 201, BudgetCategoryService.create(request.user, payload.dict())


@budget_categories_router.patch(
    "/{uuid}/",
    response={200: BudgetCategoryOut, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_categories_partial_update",
)
def partial_update_category(
    request: HttpRequest, uuid: UUID4, payload: BudgetCategoryPatchIn
) -> Any:
    """
    Corrige o título, ou altera o valor dos gastos planejados.
    Evita sobrescrições acidentais errôneas em outras rotas.
    """
    instance = BudgetCategoryService.get(request.user, uuid)
    return BudgetCategoryService.partial_update(
        request.user, instance, payload.dict(exclude_unset=True)
    )


@budget_categories_router.delete(
    "/{uuid}/",
    response={204: None, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_categories_delete",
)
def delete_category(request: HttpRequest, uuid: UUID4) -> Any:
    """
    Fecha um agrupamento no orçamento permanentemente.
    Exclui anotações de faturas de modo destrutivo para balanceamento.
    """
    instance = BudgetCategoryService.get(request.user, uuid)
    BudgetCategoryService.delete(request.user, instance)
    return 204, None
