from django.db.models import QuerySet
from ninja import File, Router, UploadedFile
from ninja.pagination import paginate
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.logistics.models.contract import Contract
from apps.logistics.schemas import (
    ContractIn,
    ContractOut,
    ContractPatchIn,
    ContractStatusTransitionIn,
)
from apps.logistics.services.contract_service import ContractService
from apps.users.types import AuthRequest


PDF_FILE_REQUIRED = File(...)


contracts_router = Router(tags=["Logistics"])


@contracts_router.get(
    "/", response=list[ContractOut], operation_id="logistics_contracts_list"
)
@paginate
def list_contracts(
    request: AuthRequest,
    wedding_id: UUID4 | None = None,
    status: str | None = None,
    supplier_id: UUID4 | None = None,
) -> QuerySet[Contract]:
    """
    Lista os contratos de fornecedores associados aos casamentos do Planner.
    Permite filtrar por casamento, status e fornecedor.
    """
    return ContractService.list(
        company=request.user.company,
        wedding_id=wedding_id,
        status=status,
        supplier_id=supplier_id,
    )


@contracts_router.get(
    "/{uuid:uuid}/",
    response={200: ContractOut, **READ_ERROR_RESPONSES},
    operation_id="logistics_contracts_read",
)
def retrieve_contract(request: AuthRequest, uuid: UUID4) -> Contract:
    """
    Exibe as cláusulas e informações completas de um contrato.
    """
    return ContractService.get(company=request.user.company, uuid=uuid)


@contracts_router.post(
    "/",
    response={201: ContractOut, **MUTATION_ERROR_RESPONSES},
    operation_id="logistics_contracts_create",
)
def create_contract(request: AuthRequest, payload: ContractIn) -> tuple[int, Contract]:
    """
    Associa um fornecedor a um casamento através de um novo contrato logístico.
    """
    contract = ContractService.create(
        company=request.user.company, data=payload.model_dump()
    )
    return 201, contract


@contracts_router.patch(
    "/{uuid:uuid}/",
    response={200: ContractOut, **MUTATION_ERROR_RESPONSES},
    operation_id="logistics_contracts_update",
)
def update_contract(
    request: AuthRequest, uuid: UUID4, payload: ContractPatchIn
) -> Contract:
    """
    Altera o status, valores agregados ou observações de um contrato existente na base.
    """
    contract = ContractService.get(company=request.user.company, uuid=uuid)
    data = payload.model_dump(exclude_unset=True)
    return ContractService.update(
        company=request.user.company, instance=contract, data=data
    )


@contracts_router.delete(
    "/{uuid:uuid}/",
    response={204: None, **MUTATION_ERROR_RESPONSES},
    operation_id="logistics_contracts_delete",
)
def delete_contract(request: AuthRequest, uuid: UUID4) -> tuple[int, None]:
    """
    Deleta o contrato e rompe o vínculo entre o fornecedor e a organização do evento.
    """
    contract = ContractService.get(company=request.user.company, uuid=uuid)
    ContractService.delete(company=request.user.company, instance=contract)
    return 204, None


@contracts_router.post(
    "/{uuid:uuid}/upload/",
    response={200: ContractOut, **MUTATION_ERROR_RESPONSES},
    operation_id="logistics_contracts_upload",
)
def upload_contract_file(
    request: AuthRequest, uuid: UUID4, pdf_file: UploadedFile = PDF_FILE_REQUIRED
) -> Contract:
    """
    Faz upload de um arquivo (PDF, DOCX, etc.) para o contrato.
    """
    contract = ContractService.upload_file(
        company=request.user.company, uuid=uuid, uploaded_file=pdf_file
    )
    return contract


@contracts_router.delete(
    "/{uuid:uuid}/upload/",
    response={204: None, **MUTATION_ERROR_RESPONSES},
    operation_id="logistics_contracts_delete_upload",
)
def delete_contract_file(request: AuthRequest, uuid: UUID4) -> tuple[int, None]:
    """
    Remove o arquivo vinculado ao contrato.
    """
    ContractService.delete_file(company=request.user.company, uuid=uuid)
    return 204, None


@contracts_router.post(
    "/{uuid:uuid}/transition-status/",
    response={200: ContractOut, **MUTATION_ERROR_RESPONSES},
    operation_id="logistics_contracts_transition_status",
)
def transition_contract_status(
    request: AuthRequest, uuid: UUID4, payload: ContractStatusTransitionIn
) -> Contract:
    """
    Transita o status do contrato (DRAFT → PENDING → SIGNED → CANCELED).
    """
    contract = ContractService.get(company=request.user.company, uuid=uuid)
    return ContractService.transition_status(
        company=request.user.company,
        instance=contract,
        new_status=payload.status,
    )
