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
from apps.logistics.models import Contract
from apps.logistics.schemas import (
    ContractIn,
    ContractOut,
    ContractPatchIn,
)
from apps.logistics.services import ContractService


@api_controller("/logistics/contracts", tags=["Logistics"])
class ContractController(ControllerBase):
    def __init__(self, service: ContractService):
        self.service = service

    @http_get("/", response=list[ContractOut], operation_id="logistics_contracts_list")
    @paginate
    def list_contracts(self, wedding_id: UUID4 | None = None) -> QuerySet[Contract]:
        """Lista contratos do Planner."""
        return self.service.list(self.context.request.user, wedding_id=wedding_id)

    @http_get(
        "/{uuid}/",
        response={200: ContractOut, **READ_ERROR_RESPONSES},
        operation_id="logistics_contracts_read",
    )
    def retrieve_contract(self, uuid: UUID4) -> Contract:
        """Retorna detalhes de um contrato."""
        return self.service.get(self.context.request.user, uuid=uuid)

    @http_post(
        "/",
        response={201: ContractOut, **MUTATION_ERROR_RESPONSES},
        operation_id="logistics_contracts_create",
    )
    def create_contract(self, payload: ContractIn) -> tuple[int, Contract]:
        """Cria um contrato vinculado a um orçamento."""
        contract = self.service.create(self.context.request.user, payload.model_dump())
        return 201, contract

    @http_patch(
        "/{uuid}/",
        response={200: ContractOut, **MUTATION_ERROR_RESPONSES},
        operation_id="logistics_contracts_partial_update",
    )
    def partial_update_contract(
        self, uuid: UUID4, payload: ContractPatchIn
    ) -> Contract:
        """Atualiza parcialmente um contrato."""
        instance = self.service.get(self.context.request.user, uuid=uuid)
        return self.service.partial_update(
            self.context.request.user, instance, payload.model_dump(exclude_unset=True)
        )

    @http_delete(
        "/{uuid}/",
        response={204: None, **MUTATION_ERROR_RESPONSES},
        operation_id="logistics_contracts_delete",
    )
    def delete_contract(self, uuid: UUID4) -> tuple[int, None]:
        """Remove um contrato."""
        self.service.delete(self.context.request.user, uuid)
        return 204, None
