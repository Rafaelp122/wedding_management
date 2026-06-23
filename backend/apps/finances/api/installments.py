from datetime import date

from django.db.models import QuerySet
from ninja import Router
from ninja.pagination import paginate
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.finances.models.installment import Installment
from apps.finances.schemas import (
    InstallmentAdjustIn,
    InstallmentOut,
)
from apps.finances.services.installment_service import InstallmentService
from apps.users.auth import require_user
from apps.users.types import AuthRequest


installments_router = Router(tags=["Finances"])


@installments_router.get(
    "/", response=list[InstallmentOut], operation_id="finances_installments_list"
)
@paginate
def list_installments(
    request: AuthRequest,
    wedding_id: UUID4 | None = None,
    expense_id: UUID4 | None = None,
    status: str | None = None,
    due_date_gte: date | None = None,
    due_date_lte: date | None = None,
) -> QuerySet[Installment]:
    """
    Lista parcelas com filtros opcionais por casamento, despesa,
    status e período de vencimento.
    """
    user = require_user(request.user)
    return InstallmentService.list(
        user.company,
        wedding_id=wedding_id,
        expense_id=expense_id,
        status=status,
        due_date_gte=due_date_gte,
        due_date_lte=due_date_lte,
    )


@installments_router.get(
    "/{uuid}/",
    response={200: InstallmentOut, **READ_ERROR_RESPONSES},
    operation_id="finances_installments_read",
)
def get_installment(request: AuthRequest, uuid: UUID4) -> Installment:
    """
    Retorna os detalhes de uma parcela específica.
    """
    user = require_user(request.user)
    return InstallmentService.get(user.company, uuid)


@installments_router.post(
    "/{uuid}/mark-as-paid/",
    response={200: InstallmentOut, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_installments_mark_as_paid",
)
def mark_as_paid_installment(request: AuthRequest, uuid: UUID4) -> Installment:
    """
    Marca uma parcela como paga (data de hoje).
    Bloqueia se já estiver paga (BR-F06).
    """
    user = require_user(request.user)
    instance = InstallmentService.get(user.company, uuid)
    return InstallmentService.mark_as_paid(user.company, instance)


@installments_router.post(
    "/{uuid}/unmark-as-paid/",
    response={200: InstallmentOut, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_installments_unmark_as_paid",
)
def unmark_as_paid_installment(request: AuthRequest, uuid: UUID4) -> Installment:
    """
    Desmarca uma parcela paga, revertendo para PENDING ou OVERDUE.
    """
    user = require_user(request.user)
    instance = InstallmentService.get(user.company, uuid)
    return InstallmentService.unmark_as_paid(user.company, instance)


@installments_router.patch(
    "/{uuid}/adjust/",
    response={200: InstallmentOut, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_installments_adjust",
)
def adjust_installment(
    request: AuthRequest, uuid: UUID4, payload: InstallmentAdjustIn
) -> Installment:
    """
    Ajusta data/valor de uma parcela futura não paga.
    Valida que due_date não pode ser anterior à parcela anterior.
    """
    user = require_user(request.user)
    instance = InstallmentService.get(user.company, uuid)
    return InstallmentService.adjust(user.company, instance, payload)
