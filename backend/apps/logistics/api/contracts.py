import json
from typing import Any

from django.db.models import QuerySet
from ninja import File, Form, Router, UploadedFile
from ninja.pagination import paginate
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.logistics.models.contract import Contract
from apps.logistics.schemas import (
    ContractFullCreateIn,
    ContractIn,
    ContractOut,
    ContractPatchIn,
    ContractStatusTransitionIn,
)
from apps.logistics.services.contract_service import ContractService
from apps.users.types import AuthRequest


PDF_FILE_REQUIRED = File(...)
CONTRACT_FULL_FORM = Form(...)
CONTRACT_FULL_FILE = File(None)


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


@contracts_router.post(
    "/full/",
    response={201: ContractOut, **MUTATION_ERROR_RESPONSES},
    operation_id="logistics_contracts_create_full",
)
def create_contract_full(
    request: AuthRequest,
    payload: ContractFullCreateIn = CONTRACT_FULL_FORM,
    pdf_file: UploadedFile | None = CONTRACT_FULL_FILE,
) -> tuple[int, Contract]:
    """
    Cria contrato com arquivo, itens e despesa em uma única transação atômica.
    """
    contract_data = payload.model_dump(
        exclude={
            "items_data",
            "create_expense",
            "expense_category",
            "expense_num_installments",
            "expense_first_due_date",
        }
    )

    items_list: list[dict[str, Any]] = json.loads(payload.items_data or "[]")

    expense_data: dict[str, Any] | None = None
    if payload.create_expense:
        expense_data = {
            "category": payload.expense_category,
            "contract": None,
            "name": contract_data.get("name", ""),
            "description": contract_data.get("description", ""),
            "estimated_amount": contract_data.get("total_amount", 0),
            "actual_amount": contract_data.get("total_amount", 0),
            "num_installments": payload.expense_num_installments,
            "first_due_date": payload.expense_first_due_date,
        }

    contract = ContractService.create_full(
        company=request.user.company,
        contract_data=contract_data,
        items_data=items_list,
        expense_data=expense_data,
        pdf_file=pdf_file,
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
