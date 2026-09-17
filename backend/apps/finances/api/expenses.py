from django.db.models import QuerySet
from ninja.pagination import paginate
from ninja_extra import Router
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.finances.models.expense import Expense
from apps.finances.schemas import (
    ExpenseFromDocumentOut,
    ExpenseIn,
    ExpenseOut,
    ExpensePatchIn,
    ExpenseRenegotiateIn,
)
from apps.finances.selectors import expense_get_selector, expense_list_selector
from apps.finances.services.expense_service import ExpenseService
from apps.users.types import AuthRequest


expenses_router = Router(tags=["Finances"])


@expenses_router.get(
    "/", response=list[ExpenseOut], operation_id="finances_expenses_list"
)
@paginate
def list_expenses(
    request: AuthRequest, wedding_id: UUID4 | None = None
) -> QuerySet[Expense]:
    """
    Lista todas as compras e despachos que saíram dos painéis orçamentários.
    """
    user = request.user
    return expense_list_selector(company=user.company, wedding_id=wedding_id)


@expenses_router.get(
    "/{uuid}/",
    response={200: ExpenseOut, **READ_ERROR_RESPONSES},
    operation_id="finances_expenses_read",
)
def get_expense(request: AuthRequest, uuid: UUID4) -> Expense:
    """
    Retorna recibo unitário simplificado nominal registrado no controle base.
    """
    user = request.user
    return expense_get_selector(company=user.company, uuid=uuid)


@expenses_router.post(
    "/",
    response={201: ExpenseOut, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_expenses_create",
)
def create_expense(request: AuthRequest, payload: ExpenseIn) -> tuple[int, Expense]:
    """
    Aprova lançamento final nos tetos das divisões e categorias.
    Consome o limite orçamentário previsto inicial geral da categoria.
    """
    user = request.user
    created = ExpenseService.create(user.company, payload)
    return 201, expense_get_selector(company=user.company, uuid=created.uuid)


@expenses_router.patch(
    "/{uuid}/",
    response={200: ExpenseOut, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_expenses_update",
)
def update_expense(
    request: AuthRequest, uuid: UUID4, payload: ExpensePatchIn
) -> Expense:
    """
    Ajuste na conta para valores fracionários sem afetar o fluxo contábil.
    """
    user = request.user
    instance = expense_get_selector(company=user.company, uuid=uuid)
    ExpenseService.update(user.company, instance, payload)
    return expense_get_selector(company=user.company, uuid=instance.uuid)


@expenses_router.delete(
    "/{uuid}/",
    response={204: None, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_expenses_delete",
)
def delete_expense(request: AuthRequest, uuid: UUID4) -> tuple[int, None]:
    """
    Deleta uma compra revertendo seu efeito, estornando em painel os gastos.
    """
    user = request.user
    instance = expense_get_selector(company=user.company, uuid=uuid)
    ExpenseService.delete(user.company, instance)
    return 204, None


@expenses_router.post(
    "/from-document/{uuid:uuid}/",
    response={200: ExpenseFromDocumentOut, **READ_ERROR_RESPONSES},
    operation_id="finances_expenses_from_document",
)
def from_document(request: AuthRequest, uuid: UUID4) -> ExpenseFromDocumentOut:
    """
    Retorna sugestão de payload para criar despesa a partir de um contrato.
    Pré-preenche valores, descrição e fornecedor do documento de referência.
    """
    user = request.user
    data = ExpenseService.from_document(company=user.company, contract_uuid=uuid)
    return ExpenseFromDocumentOut(**data)


@expenses_router.post(
    "/{uuid:uuid}/renegotiate/",
    response={200: ExpenseOut, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_expenses_renegotiate",
)
def renegotiate_expense(
    request: AuthRequest, uuid: UUID4, payload: ExpenseRenegotiateIn
) -> Expense:
    """
    Renegocia e redistribui as parcelas de uma despesa.
    Bloqueia a operação se houver parcelas já marcadas como pagas (BR-F04).
    """
    user = request.user
    instance = expense_get_selector(company=user.company, uuid=uuid)
    ExpenseService.renegotiate_installments(
        company=user.company,
        expense=instance,
        num_installments=payload.num_installments,
        first_due_date=payload.first_due_date,
    )
    return expense_get_selector(company=user.company, uuid=instance.uuid)
