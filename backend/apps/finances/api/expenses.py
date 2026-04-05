from typing import Any

from django.http import HttpRequest
from ninja import Router
from ninja.pagination import paginate
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.finances.schemas import ExpenseIn, ExpenseOut, ExpensePatchIn
from apps.finances.services.expense_service import ExpenseService


expenses_router = Router(tags=["Finances"])


@expenses_router.get(
    "/", response=list[ExpenseOut], operation_id="finances_expenses_list"
)
@paginate
def list_expenses(request: HttpRequest) -> Any:
    """
    Lista todas as compras e despachos que saíram dos painéis orçamentários.
    """
    return ExpenseService.list(request.user)


@expenses_router.get(
    "/{uuid}/",
    response={200: ExpenseOut, **READ_ERROR_RESPONSES},
    operation_id="finances_expenses_read",
)
def get_expense(request: HttpRequest, uuid: UUID4) -> Any:
    """
    Retorna recibo unitário simplificado nominal registrado no controle base.
    """
    return ExpenseService.get(request.user, uuid)


@expenses_router.post(
    "/",
    response={201: ExpenseOut, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_expenses_create",
)
def create_expense(request: HttpRequest, payload: ExpenseIn) -> Any:
    """
    Aprova lançamento final nos tetos das divisões e categorias.
    Consome o limite orçamentário previsto inicial geral da categoria.
    """
    return 201, ExpenseService.create(request.user, payload.dict())


@expenses_router.patch(
    "/{uuid}/",
    response={200: ExpenseOut, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_expenses_partial_update",
)
def partial_update_expense(
    request: HttpRequest, uuid: UUID4, payload: ExpensePatchIn
) -> Any:
    """
    Ajuste na conta para valores fracionários sem afetar o fluxo contábil.
    """
    instance = ExpenseService.get(request.user, uuid)
    return ExpenseService.partial_update(
        request.user, instance, payload.dict(exclude_unset=True)
    )


@expenses_router.delete(
    "/{uuid}/",
    response={204: None, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_expenses_delete",
)
def delete_expense(request: HttpRequest, uuid: UUID4) -> Any:
    """
    Deleta uma compra revertendo seu efeito, estornando em painel os gastos.
    """
    instance = ExpenseService.get(request.user, uuid)
    ExpenseService.delete(request.user, instance)
    return 204, None
