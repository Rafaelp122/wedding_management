from django.db.models import QuerySet
from ninja.pagination import paginate
from ninja_extra import (
    ControllerBase,
    api_controller,
    http_delete,
    http_get,
    http_patch,
    http_post,
)
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.finances.models import Installment
from apps.finances.schemas import (
    InstallmentIn,
    InstallmentOut,
    InstallmentPatchIn,
)
from apps.finances.services import InstallmentService


@api_controller("/finances/installments", tags=["Finances"])
class InstallmentController(ControllerBase):
    def __init__(self, service: InstallmentService):
        self.service = service

    @http_get(
        "/",
        response=list[InstallmentOut],
        operation_id="finances_installments_list",
    )
    @paginate
    def list_installments(self) -> QuerySet[Installment]:
        """Lista parcelas/pagamentos."""
        return self.service.list(self.context.request.user)

    @http_get(
        "/{uuid}/",
        response={200: InstallmentOut, **READ_ERROR_RESPONSES},
        operation_id="finances_installments_read",
    )
    def retrieve_installment(self, uuid: UUID4) -> Installment:
        """Retorna detalhes de uma parcela."""
        return self.service.get(self.context.request.user, uuid=uuid)

    @http_post(
        "/",
        response={201: InstallmentOut, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_installments_create",
    )
    def create_installment(self, payload: InstallmentIn) -> tuple[int, Installment]:
        """Cria uma nova parcela."""
        installment = self.service.create(
            self.context.request.user, payload.model_dump()
        )
        return 201, installment

    @http_patch(
        "/{uuid}/",
        response={200: InstallmentOut, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_installments_partial_update",
    )
    def partial_update_installment(
        self, uuid: UUID4, payload: InstallmentPatchIn
    ) -> Installment:
        """Atualiza parcialmente uma parcela."""
        instance = self.service.get(self.context.request.user, uuid=uuid)
        return self.service.partial_update(
            self.context.request.user, instance, payload.model_dump(exclude_unset=True)
        )

    @http_delete(
        "/{uuid}/",
        response={204: None, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_installments_delete",
    )
    def delete_installment(self, uuid: UUID4) -> tuple[int, None]:
        """Remove uma parcela."""
        self.service.delete(self.context.request.user, uuid)
        return 204, None
