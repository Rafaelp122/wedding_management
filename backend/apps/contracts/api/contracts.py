"""
Rotas da API Ninja para Contratos e Termos Aditivos (apps.contracts).
"""

from typing import Any

from django.db.models import QuerySet
from ninja.pagination import paginate
from ninja_extra import Router
from pydantic import UUID4

from apps.contracts.models import Contract, ContractAddendum
from apps.contracts.schemas import (
    ContractAddendumIn,
    ContractAddendumOut,
    ContractAddendumSignIn,
    ContractDetailAggregateOut,
    ContractFullCreateIn,
    ContractIn,
    ContractOut,
    ContractPatchIn,
    ContractSignIn,
    ContractStatusTransitionIn,
    ContractUploadIn,
    ContractUploadUrlIn,
    ContractUploadUrlOut,
)
from apps.contracts.selectors import (
    contract_addendum_list_selector,
    contract_detail_aggregate_selector,
    contract_get_selector,
    contract_list_selector,
)
from apps.contracts.services import ContractAddendumService, ContractService
from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.users.types import AuthRequest


contracts_router = Router(tags=["Contracts"])


@contracts_router.get("/", response=list[ContractOut], operation_id="contracts_list")
@paginate
def list_contracts(
    request: AuthRequest,
    wedding_id: UUID4 | None = None,
    status: str | None = None,
    contract_type: str | None = None,
    supplier_id: UUID4 | None = None,
    client_id: UUID4 | None = None,
    parent_id: UUID4 | None = None,
) -> QuerySet[Contract]:
    """Lista contratos associados aos casamentos do usuário autenticado."""
    user = request.user
    return contract_list_selector(
        company=user.company,
        wedding_id=wedding_id,
        status=status,
        contract_type=contract_type,
        supplier_id=supplier_id,
        client_id=client_id,
        parent_id=parent_id,
    )


@contracts_router.get(
    "/{uuid:uuid}/details/",
    response={200: ContractDetailAggregateOut, **READ_ERROR_RESPONSES},
    operation_id="contracts_details_read",
)
def retrieve_contract_details(request: AuthRequest, uuid: UUID4) -> dict[str, Any]:
    """Exibe cláusulas, itens e termos aditivos agregados de um contrato."""
    user = request.user
    return contract_detail_aggregate_selector(company=user.company, contract_uuid=uuid)


@contracts_router.get(
    "/{uuid:uuid}/",
    response={200: ContractOut, **READ_ERROR_RESPONSES},
    operation_id="contracts_read",
)
def retrieve_contract(request: AuthRequest, uuid: UUID4) -> Contract:
    """Exibe cláusulas e dados cadastrais completos de um contrato."""
    user = request.user
    return contract_get_selector(company=user.company, uuid=uuid)


@contracts_router.post(
    "/upload-url/",
    response={200: ContractUploadUrlOut, **MUTATION_ERROR_RESPONSES},
    operation_id="contracts_upload_url",
)
def generate_upload_url(
    request: AuthRequest, payload: ContractUploadUrlIn
) -> ContractUploadUrlOut:
    """Gera URL pré-assinada para upload direto de arquivo no Storage."""
    user = request.user
    result = ContractService.generate_upload_url(
        company=user.company,
        wedding_id=payload.wedding_id,
        filename=payload.filename,
    )
    return ContractUploadUrlOut(
        upload_url=result["upload_url"], object_key=result["object_key"]
    )


@contracts_router.post(
    "/{uuid:uuid}/upload/",
    response={200: ContractOut, **MUTATION_ERROR_RESPONSES},
    operation_id="contracts_upload_file",
)
def upload_contract_file(
    request: AuthRequest, uuid: UUID4, payload: ContractUploadIn
) -> Contract:
    """Associa a chave de um arquivo enviado no storage ao contrato."""
    user = request.user
    contract = contract_get_selector(company=user.company, uuid=uuid)
    return ContractService.upload_file(
        company=user.company,
        instance=contract,
        pdf_file_key=payload.pdf_file_key,
    )


@contracts_router.post(
    "/full/",
    response={201: ContractOut, **MUTATION_ERROR_RESPONSES},
    operation_id="contracts_create_full",
)
def create_full_contract(
    request: AuthRequest, payload: ContractFullCreateIn
) -> tuple[int, Contract]:
    """Cria contrato completo, itens e despesa opcional em transação atômica."""
    user = request.user
    contract = ContractService.create_full_from_payload(
        company=user.company,
        payload=payload,
    )
    return 201, contract_get_selector(company=user.company, uuid=contract.uuid)


@contracts_router.post(
    "/",
    response={201: ContractOut, **MUTATION_ERROR_RESPONSES},
    operation_id="contracts_create",
)
def create_contract(request: AuthRequest, payload: ContractIn) -> tuple[int, Contract]:
    """Cria um novo contrato básico para o casamento."""
    user = request.user
    contract = ContractService.create(company=user.company, payload=payload)
    return 201, contract_get_selector(company=user.company, uuid=contract.uuid)


@contracts_router.patch(
    "/{uuid:uuid}/",
    response={200: ContractOut, **MUTATION_ERROR_RESPONSES},
    operation_id="contracts_update",
)
def update_contract(
    request: AuthRequest, uuid: UUID4, payload: ContractPatchIn
) -> Contract:
    """Atualiza parcialmente os campos de um contrato existente."""
    user = request.user
    contract = contract_get_selector(company=user.company, uuid=uuid)
    ContractService.update(
        company=user.company,
        instance=contract,
        payload=payload,
    )
    return contract_get_selector(company=user.company, uuid=uuid)


@contracts_router.delete(
    "/{uuid:uuid}/",
    response={204: None, **MUTATION_ERROR_RESPONSES},
    operation_id="contracts_delete",
)
def delete_contract(request: AuthRequest, uuid: UUID4) -> tuple[int, None]:
    """Exclui um contrato do sistema garantindo validações de integridade."""
    user = request.user
    contract = contract_get_selector(company=user.company, uuid=uuid)
    ContractService.delete(company=user.company, instance=contract)
    return 204, None


@contracts_router.post(
    "/{uuid:uuid}/sign/",
    response={200: ContractOut, **MUTATION_ERROR_RESPONSES},
    operation_id="contracts_sign",
)
def sign_contract(
    request: AuthRequest, uuid: UUID4, payload: ContractSignIn | None = None
) -> Contract:
    """Formaliza a assinatura do contrato."""
    user = request.user
    contract = contract_get_selector(company=user.company, uuid=uuid)
    signed_date = payload.signed_date if payload else None
    pdf_file_key = payload.pdf_file_key if payload else None
    ContractService.sign(
        company=user.company,
        instance=contract,
        signed_date=signed_date,
        pdf_file=pdf_file_key,
    )
    return contract_get_selector(company=user.company, uuid=uuid)


@contracts_router.post(
    "/{uuid:uuid}/transition/",
    response={200: ContractOut, **MUTATION_ERROR_RESPONSES},
    operation_id="contracts_status_transition",
)
def transition_contract_status(
    request: AuthRequest, uuid: UUID4, payload: ContractStatusTransitionIn
) -> Contract:
    """Executa a transição de status do contrato."""
    user = request.user
    contract = contract_get_selector(company=user.company, uuid=uuid)
    ContractService.transition_status(
        company=user.company,
        instance=contract,
        target_status=payload.status,
    )
    return contract_get_selector(company=user.company, uuid=uuid)


@contracts_router.post(
    "/{uuid:uuid}/send-to-pending/",
    response={200: ContractOut, **MUTATION_ERROR_RESPONSES},
    operation_id="contracts_send_to_pending",
)
def send_contract_to_pending(request: AuthRequest, uuid: UUID4) -> Contract:
    """Envia o contrato para assinatura externa."""
    user = request.user
    contract = contract_get_selector(company=user.company, uuid=uuid)
    ContractService.send_to_pending(company=user.company, instance=contract)
    return contract_get_selector(company=user.company, uuid=uuid)


@contracts_router.post(
    "/{uuid:uuid}/cancel/",
    response={200: ContractOut, **MUTATION_ERROR_RESPONSES},
    operation_id="contracts_cancel",
)
def cancel_contract(request: AuthRequest, uuid: UUID4) -> Contract:
    """Cancela formalmente o contrato."""
    user = request.user
    contract = contract_get_selector(company=user.company, uuid=uuid)
    ContractService.cancel(company=user.company, instance=contract)
    return contract_get_selector(company=user.company, uuid=uuid)


@contracts_router.post(
    "/{uuid:uuid}/revert-to-draft/",
    response={200: ContractOut, **MUTATION_ERROR_RESPONSES},
    operation_id="contracts_revert_to_draft",
)
def revert_contract_to_draft(request: AuthRequest, uuid: UUID4) -> Contract:
    """Reverte o contrato para rascunho de trabalho."""
    user = request.user
    contract = contract_get_selector(company=user.company, uuid=uuid)
    ContractService.revert_to_draft(company=user.company, instance=contract)
    return contract_get_selector(company=user.company, uuid=uuid)


@contracts_router.post(
    "/{uuid:uuid}/detach-file/",
    response={200: ContractOut, **MUTATION_ERROR_RESPONSES},
    operation_id="contracts_detach_file",
)
def detach_contract_file(request: AuthRequest, uuid: UUID4) -> Contract:
    """Remove o anexo PDF de um contrato não assinado."""
    user = request.user
    contract = contract_get_selector(company=user.company, uuid=uuid)
    ContractService.detach_file(company=user.company, instance=contract)
    return contract_get_selector(company=user.company, uuid=uuid)


@contracts_router.get(
    "/{uuid:contract_id}/addendums/",
    response=list[ContractAddendumOut],
    operation_id="contracts_addendums_list",
)
def list_contract_addendums(
    request: AuthRequest, contract_id: UUID4
) -> QuerySet[ContractAddendum]:
    """Lista todos os termos aditivos pertencentes ao contrato."""
    user = request.user
    return contract_addendum_list_selector(
        company=user.company,
        contract_uuid=contract_id,
    )


@contracts_router.post(
    "/{uuid:contract_id}/addendums/",
    response={201: ContractAddendumOut, **MUTATION_ERROR_RESPONSES},
    operation_id="contracts_addendums_create",
)
def create_contract_addendum(
    request: AuthRequest,
    contract_id: UUID4,
    payload: ContractAddendumIn,
) -> tuple[int, ContractAddendum]:
    """Cria um novo termo aditivo formalizado vinculado ao contrato."""
    user = request.user
    addendum = ContractAddendumService.create(
        company=user.company,
        contract_id=contract_id,
        payload=payload,
    )
    return 201, addendum


@contracts_router.post(
    "/{uuid:contract_id}/addendums/{uuid:addendum_id}/sign/",
    response={200: ContractAddendumOut, **MUTATION_ERROR_RESPONSES},
    operation_id="contracts_addendums_sign",
)
def sign_contract_addendum(
    request: AuthRequest,
    contract_id: UUID4,
    addendum_id: UUID4,
    payload: ContractAddendumSignIn | None = None,
) -> ContractAddendum:
    """Formaliza a assinatura de um termo aditivo e atualiza despesa vinculada."""
    user = request.user
    return ContractAddendumService.sign(
        company=user.company,
        contract_id=contract_id,
        addendum_id=addendum_id,
        payload=payload,
    )


@contracts_router.post(
    "/{uuid:contract_id}/addendums/{uuid:addendum_id}/cancel/",
    response={200: ContractAddendumOut, **MUTATION_ERROR_RESPONSES},
    operation_id="contracts_addendums_cancel",
)
def cancel_contract_addendum(
    request: AuthRequest,
    contract_id: UUID4,
    addendum_id: UUID4,
) -> ContractAddendum:
    """Cancela um termo aditivo formalmente."""
    user = request.user
    return ContractAddendumService.cancel(
        company=user.company,
        contract_id=contract_id,
        addendum_id=addendum_id,
    )


@contracts_router.delete(
    "/{uuid:contract_id}/addendums/{uuid:addendum_id}/",
    response={204: None, **MUTATION_ERROR_RESPONSES},
    operation_id="contracts_addendums_delete",
)
def delete_contract_addendum(
    request: AuthRequest,
    contract_id: UUID4,
    addendum_id: UUID4,
) -> tuple[int, None]:
    """Exclui um termo aditivo em estado pendente."""
    user = request.user
    ContractAddendumService.delete(
        company=user.company,
        contract_id=contract_id,
        addendum_id=addendum_id,
    )
    return 204, None
