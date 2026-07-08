import json
from typing import Any

from django.db.models import QuerySet
from ninja.pagination import paginate
from ninja_extra import Router
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.finances.schemas import ExpenseIn
from apps.logistics.models.contract import Contract
from apps.logistics.schemas import (
    ContractFullCreateIn,
    ContractIn,
    ContractOut,
    ContractPatchIn,
    ContractStatusTransitionIn,
    ContractUploadIn,
    ContractUploadUrlIn,
    ContractUploadUrlOut,
    ItemIn,
)
from apps.logistics.services.contract_service import ContractService
from apps.users.auth import require_user
from apps.users.types import AuthRequest


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
    parent_id: UUID4 | None = None,
) -> QuerySet[Contract]:
    """
    Lista os contratos de fornecedores associados aos casamentos do Planner.
    Permite filtrar por casamento, status, fornecedor e contrato pai (aditivos).
    """
    user = require_user(request.user)
    return ContractService.list(
        company=user.company,
        wedding_id=wedding_id,
        status=status,
        supplier_id=supplier_id,
        parent_id=parent_id,
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
    user = require_user(request.user)
    return ContractService.get(company=user.company, uuid=uuid)


@contracts_router.post(
    "/upload-url/",
    response={200: ContractUploadUrlOut, **MUTATION_ERROR_RESPONSES},
    operation_id="logistics_contracts_upload_url",
)
def generate_upload_url(
    request: AuthRequest, payload: ContractUploadUrlIn
) -> ContractUploadUrlOut:
    """
    Gera uma URL pré-assinada para upload direto de um arquivo PDF/imagem para o R2/S3.
    """
    user = require_user(request.user)
    res = ContractService.generate_upload_url(
        company=user.company,
        filename=payload.filename,
        wedding_id=payload.wedding_id,
    )
    return ContractUploadUrlOut(**res)


@contracts_router.post(
    "/",
    response={201: ContractOut, **MUTATION_ERROR_RESPONSES},
    operation_id="logistics_contracts_create",
)
def create_contract(request: AuthRequest, payload: ContractIn) -> tuple[int, Contract]:
    """
    Associa um fornecedor a um casamento através de um novo contrato logístico.
    """
    user = require_user(request.user)
    contract = ContractService.create(company=user.company, payload=payload)
    return 201, contract


@contracts_router.post(
    "/full/",
    response={201: ContractOut, **MUTATION_ERROR_RESPONSES},
    operation_id="logistics_contracts_create_full",
)
def create_contract_full(
    request: AuthRequest,
    payload: ContractFullCreateIn,
) -> tuple[int, Contract]:
    """
    Cria contrato com arquivo, itens e despesa em uma única transação atômica.
    """
    user = require_user(request.user)

    contract_in = ContractIn(
        wedding=payload.wedding,
        supplier=payload.supplier,
        name=payload.name,
        total_amount=payload.total_amount,
        status=payload.status,
        description=payload.description,
        parent=payload.parent,
    )

    items_list: list[ItemIn] = []
    raw_items: list[dict[str, Any]] = json.loads(payload.items_data or "[]")
    for item_dict in raw_items:
        item_dict["wedding"] = payload.wedding
        items_list.append(ItemIn(**item_dict))

    expense_in: ExpenseIn | None = None
    if payload.create_expense:
        expense_in = ExpenseIn(
            category=payload.expense_category,  # type: ignore[arg-type]
            name=payload.name,
            description=payload.description,
            estimated_amount=payload.total_amount,
            actual_amount=payload.total_amount,
            num_installments=payload.expense_num_installments,
            first_due_date=payload.expense_first_due_date,
        )

    contract = ContractService.create_full(
        company=user.company,
        contract_data=contract_in,
        items_data=items_list or None,
        expense_data=expense_in,
        pdf_file_key=payload.pdf_file_key,
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
    user = require_user(request.user)
    contract = ContractService.get(company=user.company, uuid=uuid)
    return ContractService.update(
        company=user.company, instance=contract, payload=payload
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
    user = require_user(request.user)
    contract = ContractService.get(company=user.company, uuid=uuid)
    ContractService.delete(company=user.company, instance=contract)
    return 204, None


@contracts_router.post(
    "/{uuid:uuid}/upload/",
    response={200: ContractOut, **MUTATION_ERROR_RESPONSES},
    operation_id="logistics_contracts_upload",
)
def upload_contract_file(
    request: AuthRequest, uuid: UUID4, payload: ContractUploadIn
) -> Contract:
    """
    Associa um arquivo já carregado no R2/S3 (chave) ao contrato.
    """
    user = require_user(request.user)
    contract = ContractService.upload_file(
        company=user.company, uuid=uuid, pdf_file_key=payload.pdf_file_key
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
    user = require_user(request.user)
    ContractService.delete_file(company=user.company, uuid=uuid)
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
    user = require_user(request.user)
    contract = ContractService.get(company=user.company, uuid=uuid)
    return ContractService.transition_status(
        company=user.company,
        instance=contract,
        new_status=payload.status,
    )
