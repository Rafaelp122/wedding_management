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
) -> QuerySet[Installment]:
    """
    Lista parcelas com filtro opcional por casamento e despesa.
    """
    return InstallmentService.list(
        request.user.company, wedding_id=wedding_id, expense_id=expense_id
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
    return InstallmentService.get(request.user.company, uuid)


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
    instance = InstallmentService.get(request.user.company, uuid)
    return InstallmentService.mark_as_paid(request.user.company, instance)


@installments_router.post(
    "/{uuid}/unmark-as-paid/",
    response={200: InstallmentOut, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_installments_unmark_as_paid",
)
def unmark_as_paid_installment(request: AuthRequest, uuid: UUID4) -> Installment:
    """
    Desmarca uma parcela paga, revertendo para PENDING ou OVERDUE.
    """
    instance = InstallmentService.get(request.user.company, uuid)
    return InstallmentService.unmark_as_paid(request.user.company, instance)


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
    instance = InstallmentService.get(request.user.company, uuid)
    return InstallmentService.adjust(
        request.user.company,
        instance,
        payload.dict(exclude_unset=True, exclude_none=True),
    )
