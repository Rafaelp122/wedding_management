from django.db.models import QuerySet
from django.http import HttpRequest
from ninja import Router
from ninja.pagination import paginate
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.finances.models.installment import Installment
from apps.finances.schemas import InstallmentIn, InstallmentOut, InstallmentPatchIn
from apps.finances.services.installment_service import InstallmentService


installments_router = Router(tags=["Finances"])


@installments_router.get(
    "/", response=list[InstallmentOut], operation_id="finances_installments_list"
)
@paginate
def list_installments(request: HttpRequest) -> QuerySet[Installment]:
    """
    Lista faturas fragmentadas originárias para os fluxos pendentes.
    Faturas isoladas ligadas a pagamentos unificados.
    """
    return InstallmentService.list(request.user)


@installments_router.get(
    "/{uuid}/",
    response={200: InstallmentOut, **READ_ERROR_RESPONSES},
    operation_id="finances_installments_read",
)
def get_installment(request: HttpRequest, uuid: UUID4) -> Installment:
    """
    Revela notas fragmentais e guias pendentes programados do recebimento.
    """
    return InstallmentService.get(request.user, uuid)


@installments_router.post(
    "/",
    response={201: InstallmentOut, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_installments_create",
)
def create_installment(
    request: HttpRequest, payload: InstallmentIn
) -> tuple[int, Installment]:
    """
    Grava pendências parciais atestando dependências de transações.
    """
    return 201, InstallmentService.create(request.user, payload.dict())


@installments_router.patch(
    "/{uuid}/",
    response={200: InstallmentOut, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_installments_partial_update",
)
def partial_update_installment(
    request: HttpRequest, uuid: UUID4, payload: InstallmentPatchIn
) -> Installment:
    """
    Edita temporalmente ou encerra status validando com pagamento de guia as etapas.
    """
    instance = InstallmentService.get(request.user, uuid)
    return InstallmentService.partial_update(
        request.user, instance, payload.dict(exclude_unset=True)
    )


@installments_router.delete(
    "/{uuid}/",
    response={204: None, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_installments_delete",
)
def delete_installment(request: HttpRequest, uuid: UUID4) -> tuple[int, None]:
    """
    Exclui registro pendente restabelecendo ordem das cobranças integrando-as.
    """
    instance = InstallmentService.get(request.user, uuid)
    InstallmentService.delete(request.user, instance)
    return 204, None
