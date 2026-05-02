from django.db.models import QuerySet
from django.http import HttpRequest
from ninja import Router
from ninja.pagination import paginate
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.finances.models.expense import Expense
from apps.finances.schemas import ExpenseIn, ExpenseOut, ExpensePatchIn
from apps.finances.services.expense_service import ExpenseService


expenses_router = Router(tags=["Finances"])


@expenses_router.get(
    "/", response=list[ExpenseOut], operation_id="finances_expenses_list"
)
@paginate
def list_expenses(
    request: HttpRequest, wedding_id: UUID4 | None = None
) -> QuerySet[Expense]:
    """
    Lista todas as compras e despachos que saíram dos painéis orçamentários.
    """
    return ExpenseService.list(request.user, wedding_id=wedding_id)


@expenses_router.get(
    "/{uuid}/",
    response={200: ExpenseOut, **READ_ERROR_RESPONSES},
    operation_id="finances_expenses_read",
)
def get_expense(request: HttpRequest, uuid: UUID4) -> Expense:
    """
    Retorna recibo unitário simplificado nominal registrado no controle base.
    """
    return ExpenseService.get(request.user, uuid)


@expenses_router.post(
    "/",
    response={201: ExpenseOut, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_expenses_create",
)
def create_expense(request: HttpRequest, payload: ExpenseIn) -> tuple[int, Expense]:
    """
    Aprova lançamento final nos tetos das divisões e categorias.
    Consome o limite orçamentário previsto inicial geral da categoria.
    """
    return 201, ExpenseService.create(request.user, payload.dict())


@expenses_router.patch(
    "/{uuid}/",
    response={200: ExpenseOut, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_expenses_update",
)
def update_expense(
    request: HttpRequest, uuid: UUID4, payload: ExpensePatchIn
) -> Expense:
    """
    Ajuste na conta para valores fracionários sem afetar o fluxo contábil.
    """
    instance = ExpenseService.get(request.user, uuid)
    return ExpenseService.update(
        request.user, instance, payload.dict(exclude_unset=True)
    )


@expenses_router.delete(
    "/{uuid}/",
    response={204: None, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_expenses_delete",
)
def delete_expense(request: HttpRequest, uuid: UUID4) -> tuple[int, None]:
    """
    Deleta uma compra revertendo seu efeito, estornando em painel os gastos.
    """
    instance = ExpenseService.get(request.user, uuid)
    ExpenseService.delete(request.user, instance)
    return 204, None
