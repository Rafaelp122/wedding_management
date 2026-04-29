from typing import Any

from django.db.models import QuerySet
from ninja.pagination import paginate
from ninja_extra import ControllerBase, api_controller, route
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.logistics.dependencies import get_contract
from apps.logistics.models.contract import Contract
from apps.logistics.schemas import ContractIn, ContractOut, ContractPatchIn
from apps.logistics.services.contract_service import ContractService


@api_controller("/logistics/contracts", tags=["Logistics"])
class ContractController(ControllerBase):
    context: Any

    @route.get("/", response=list[ContractOut], operation_id="logistics_contracts_list")
    @paginate
    def list_contracts(self, event_id: UUID4 | None = None) -> QuerySet[Contract]:
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        assert self.context.request.user  # noqa: S101
        return ContractService.list(user=self.context.request.user, event_id=event_id)

    @route.get(
        "/{contract_uuid}/",
        response={200: ContractOut, **READ_ERROR_RESPONSES},
        operation_id="logistics_contracts_read",
    )
    def retrieve_contract(self, contract_uuid: UUID4) -> Contract:
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        return get_contract(self.context.request, contract_uuid)

    @route.post(
        "/",
        response={201: ContractOut, **MUTATION_ERROR_RESPONSES},
        operation_id="logistics_contracts_create",
    )
    def create_contract(self, payload: ContractIn) -> tuple[int, Contract]:
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        assert self.context.request.user  # noqa: S101
        contract = ContractService.create(
            user=self.context.request.user, data=payload.model_dump()
        )
        return 201, contract

    @route.patch(
        "/{contract_uuid}/",
        response={200: ContractOut, **MUTATION_ERROR_RESPONSES},
        operation_id="logistics_contracts_update",
    )
    def update_contract(
        self, contract_uuid: UUID4, payload: ContractPatchIn
    ) -> Contract:
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        assert self.context.request.user  # noqa: S101
        contract = get_contract(self.context.request, contract_uuid)
        return ContractService.update(
            user=self.context.request.user,
            instance=contract,
            data=payload.model_dump(exclude_unset=True),
        )

    @route.delete(
        "/{contract_uuid}/",
        response={204: None, **MUTATION_ERROR_RESPONSES},
        operation_id="logistics_contracts_delete",
    )
    def delete_contract(self, contract_uuid: UUID4) -> tuple[int, None]:
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        contract = get_contract(self.context.request, contract_uuid)
        ContractService.delete(instance=contract)
        return 204, None
