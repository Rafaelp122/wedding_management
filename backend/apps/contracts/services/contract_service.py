"""
Camada de serviço para orquestração e mutação de Contratos (ContractService).

Responsabilidade: Mutação atômica, validação de posse multitenant, integração com
Storage (R2/S3), orquestração de despesas vinculadas e itens contratuais (ADR-030 / ADR-031).
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import date
from typing import Any, cast
from uuid import UUID

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import ProtectedError

from apps.clients.interfaces import get_client_for_tenant
from apps.contracts.interfaces import get_supplier_for_company
from apps.contracts.models import Contract
from apps.contracts.schemas import (
    ContractFullCreateIn,
    ContractIn,
    ContractItemIn,
    ContractPatchIn,
)
from apps.contracts.selectors.contract_selectors import contract_get_selector
from apps.core.exceptions import (
    BusinessRuleViolation,
)
from apps.core.services.storage import (
    StorageService,
    get_storage_service,
)
from apps.core.shortcuts import get_object_or_404_for_tenant, resolve_tenant_resource
from apps.core.tenant import validate_tenant_ownership
from apps.finances.interfaces import ExpenseIn, create_expense_from_contract
from apps.logistics.interfaces import create_item_for_contract
from apps.tenants.models import Company
from apps.weddings.models import Wedding


logger = logging.getLogger(__name__)


class ContractService:
    """Camada de serviço para gestão e ciclo de vida de contratos unificados."""

    _storage_service: StorageService | None = None

    @classmethod
    def get_storage_client(cls) -> StorageService:
        """Retorna o cliente de storage ativo.

        Returns:
            A instância ativa de StorageService.
        """
        if cls._storage_service is None:
            cls._storage_service = get_storage_service()
        return cls._storage_service

    @classmethod
    def set_storage_service(cls, storage_service: StorageService) -> None:
        """Injeta uma instância customizada de StorageService.

        Args:
            storage_service: Instância customizada ou mock de StorageService.
        """
        cls._storage_service = storage_service

    @staticmethod
    @transaction.atomic
    def create_full_from_payload(
        company: Company,
        payload: ContractFullCreateIn,
    ) -> Contract:
        """Cria um contrato completo a partir do payload HTTP validado.

        Args:
            company: O tenant atual para isolamento de dados.
            payload: Dados validados da requisição.

        Returns:
            A instância do Contract criada e totalmente populada.
        """
        contract_data = ContractIn(
            wedding=payload.wedding,
            contract_type=getattr(payload, "contract_type", "SUPPLIER"),
            service_tier=getattr(payload, "service_tier", None),
            supplier=getattr(payload, "supplier", None),
            client=getattr(payload, "client", None),
            name=payload.name,
            total_amount=payload.total_amount,
            installments_count=getattr(payload, "installments_count", 1),
            status=payload.status,
            description=payload.description,
            parent=payload.parent,
        )

        items_data = ContractService._resolve_full_items_data(payload)
        expense_data = ContractService._build_full_expense_payload(payload)

        return ContractService.create_full(
            company=company,
            contract_data=contract_data,
            items_data=items_data,
            expense_data=expense_data,
            pdf_file_key=payload.pdf_file_key,
        )

    @staticmethod
    def _resolve_full_items_data(
        payload: Any,
    ) -> list[Any] | None:
        """Resolve a lista de itens a partir dos atributos do payload.

        Args:
            payload: Payload contendo itens estruturados ou serializados em JSON.

        Returns:
            Lista de schemas de item ou None se vazia.
        """
        if getattr(payload, "items", None):
            return cast("list[Any]", payload.items)

        items_data_str = getattr(payload, "items_data", None)
        if items_data_str:
            try:
                parsed_items = json.loads(items_data_str)
            except json.JSONDecodeError as e:
                raise BusinessRuleViolation(
                    detail="items_data deve ser um JSON válido.",
                    code="invalid_items_data",
                ) from e

            if not isinstance(parsed_items, list) or not all(
                isinstance(item, dict) for item in parsed_items
            ):
                raise BusinessRuleViolation(
                    detail="items_data deve ser uma lista de objetos JSON.",
                    code="invalid_items_data",
                )

            try:
                return [ContractItemIn.model_validate(item) for item in parsed_items]
            except Exception as e:
                raise BusinessRuleViolation(
                    detail="items_data contém item inválido.",
                    code="invalid_items_data",
                ) from e

        return None

    _build_full_items_payload = _resolve_full_items_data

    @staticmethod
    def _build_full_expense_payload(
        payload: ContractFullCreateIn,
    ) -> ExpenseIn | None:
        """Monta o payload financeiro opcional para criação de despesa vinculada.

        Args:
            payload: Dados recebidos pelo endpoint de criação completa.

        Returns:
            Schema de criação de despesa quando solicitado ou None.
        """
        if not payload.create_expense:
            return None

        return ExpenseIn(
            category=payload.expense_category,  # type: ignore[arg-type]
            name=payload.name,
            description=payload.description,
            estimated_amount=payload.total_amount,
            actual_amount=payload.total_amount,
            num_installments=payload.expense_num_installments,
            first_due_date=payload.expense_first_due_date,
        )

    @staticmethod
    @transaction.atomic
    def create(company: Company, payload: ContractIn) -> Contract:
        """Cria um contrato no banco de dados validando isolamento multitenant.

        Args:
            company: O tenant atual para isolamento de dados.
            payload: Objeto de entrada contendo os dados do contrato.

        Returns:
            A instância criada do Contract.

        Raises:
            BusinessRuleViolation: Se ocorrer erro de validação de modelo.
        """
        logger.info("Iniciando criação de Contrato para company_id=%s", company.id)

        data = payload.model_dump(exclude_unset=True)

        wedding_input = data.pop("wedding", None)
        supplier_input = data.pop("supplier", None)
        client_input = data.pop("client", None)
        pdf_file_key = data.pop("pdf_file_key", None)
        data.pop("parent", None)

        wedding = resolve_tenant_resource(
            Wedding,
            company,
            wedding_input,
            detail="Casamento não encontrado ou acesso negado.",
            code="wedding_not_found_or_denied",
        )

        supplier: Any | None = None
        if supplier_input:
            supplier = get_supplier_for_company(
                company=company, supplier_uuid_or_id=supplier_input
            )

        client: Any | None = None
        if client_input:
            client = get_client_for_tenant(company=company, client_id=client_input)

        contract = Contract(
            company=company,
            wedding=wedding,
            supplier=supplier,
            client=client,
            pdf_file=pdf_file_key,
            **data,
        )

        try:
            contract.save()
        except ValidationError as e:
            msg = "; ".join(e.messages) if hasattr(e, "messages") else str(e)
            raise BusinessRuleViolation(
                detail=msg,
                code="contract_creation_validation_error",
            ) from e

        logger.info("Contrato criado com sucesso: uuid=%s", contract.uuid)
        return contract

    @staticmethod
    @transaction.atomic
    def create_full(
        company: Company,
        *,
        contract_data: ContractIn,
        items_data: list[Any] | None = None,
        expense_data: ExpenseIn | None = None,
        pdf_file_key: str | None = None,
    ) -> Contract:
        """Orquestra a criação completa de um contrato com itens e despesa opcional.

        Args:
            company: O tenant atual para isolamento de dados.
            contract_data: Dados básicos do contrato.
            items_data: Lista opcional de itens a serem criados.
            expense_data: Dados opcionais da despesa para parcelamento.
            pdf_file_key: Chave do arquivo salvo no storage.

        Returns:
            A instância do Contract criada e totalmente populada.
        """
        contract = ContractService.create(company=company, payload=contract_data)

        if pdf_file_key:
            contract.attach_file(pdf_file_key)
            contract.save(update_fields=["pdf_file", "updated_at"])

        if items_data:
            for item in items_data:
                create_item_for_contract(
                    company=company,
                    payload=item,
                    contract_uuid=contract.uuid,
                    wedding_uuid=contract.wedding.uuid,
                )

        if expense_data:
            create_expense_from_contract(
                company=company,
                payload=expense_data,
                contract_uuid=contract.uuid,
            )

        return contract

    @staticmethod
    @transaction.atomic
    def update(
        company: Company,
        instance: Contract,
        payload: ContractPatchIn,
    ) -> Contract:
        """Atualiza parcialmente um contrato validando regras de domínio.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: Instância do contrato a ser atualizada.
            payload: Dados parciais validados para atualização.

        Returns:
            A instância atualizada do Contract.

        Raises:
            BusinessRuleViolation: Se ocorrer violação de regras de validação.
        """
        validate_tenant_ownership(
            company,
            instance,
            detail="Contrato não encontrado ou acesso negado.",
            code="contract_not_found_or_denied",
        )

        data = payload.model_dump(exclude_unset=True)
        updated_fields: set[str] = set()

        if "status" in data or "contract_type" in data:
            raise BusinessRuleViolation(
                detail="Status e tipo de contrato não podem ser alterados por atualização parcial. Use os endpoints dedicados de assinatura/transição.",
                code="contract_locked_field_update",
            )
        if instance.status == Contract.StatusChoices.SIGNED and "total_amount" in data:
            raise BusinessRuleViolation(
                detail="O valor de um contrato assinado só pode ser alterado via termo aditivo.",
                code="contract_signed_value_locked",
            )

        if "supplier" in data:
            sup_val = data.pop("supplier")
            instance.supplier = (
                get_supplier_for_company(company=company, supplier_uuid_or_id=sup_val)
                if sup_val
                else None
            )
            updated_fields.add("supplier")

        if "client" in data:
            cli_val = data.pop("client")
            instance.client = (
                get_client_for_tenant(company=company, client_id=cli_val)
                if cli_val
                else None
            )
            updated_fields.add("client")

        pdf_key = data.pop("pdf_file_key", None)
        if pdf_key is not None:
            instance.attach_file(pdf_key)
            updated_fields.add("pdf_file")

        data.pop("parent", None)

        for field, value in data.items():
            if field == "pdf_file" and value is None:
                continue
            setattr(instance, field, value)
            updated_fields.add(field)

        if updated_fields:
            updated_fields.add("updated_at")
            try:
                instance.save(update_fields=list(updated_fields))
            except ValidationError as e:
                msg = "; ".join(e.messages) if hasattr(e, "messages") else str(e)
                raise BusinessRuleViolation(
                    detail=msg,
                    code="contract_update_validation_error",
                ) from e

        return instance

    @staticmethod
    @transaction.atomic
    def delete(company: Company, instance: Contract) -> None:
        """Exclui um contrato do banco de dados garantindo a integridade.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: Instância do contrato a ser excluída.

        Raises:
            BusinessRuleViolation: Se o contrato estiver assinado ou houver vínculo protegido.
        """
        validate_tenant_ownership(
            company,
            instance,
            detail="Contrato não encontrado ou acesso negado.",
            code="contract_not_found_or_denied",
        )

        if instance.status == Contract.StatusChoices.SIGNED:
            raise BusinessRuleViolation(
                detail="Não é possível excluir um contrato formalmente assinado.",
                code="cannot_delete_signed_contract",
            )

        try:
            instance.delete()
        except ProtectedError as e:
            raise BusinessRuleViolation(
                detail="Não é possível excluir contrato com despesas ou itens vinculados.",
                code="contract_has_protected_dependencies",
            ) from e

    @staticmethod
    @transaction.atomic
    def sign(
        company: Company,
        instance: Contract,
        signed_date: date | None = None,
        pdf_file: Any = None,
        *,
        pdf_file_key: str | None = None,
    ) -> Contract:
        """Formaliza a assinatura do contrato.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: Instância do contrato a ser assinado.
            signed_date: Data formal da assinatura.
            pdf_file: Arquivo opcional do documento assinado.
            pdf_file_key: Chave opcional de arquivo no storage.

        Returns:
            A instância do Contract com status SIGNED.
        """
        validate_tenant_ownership(
            company,
            instance,
            detail="Contrato não encontrado ou acesso negado.",
            code="contract_not_found_or_denied",
        )

        effective_file = pdf_file if pdf_file is not None else pdf_file_key
        instance.sign(signed_date=signed_date, pdf_file=effective_file)

        updated_fields = {"status", "signed_date", "updated_at"}
        if instance.pdf_file:
            updated_fields.add("pdf_file")

        try:
            instance.save(update_fields=list(updated_fields))
        except ValidationError as e:
            msg = "; ".join(e.messages) if hasattr(e, "messages") else str(e)
            raise BusinessRuleViolation(
                detail=msg,
                code="contract_invalid_status_transition",
            ) from e

        return instance

    @staticmethod
    @transaction.atomic
    def transition_status(
        company: Company,
        instance: Contract,
        target_status: str | Contract.StatusChoices | None = None,
        *,
        new_status: str | Contract.StatusChoices | None = None,
    ) -> Contract:
        """Transita o status do contrato pelo autômato de estados.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: Instância do contrato a ter o status alterado.
            target_status: Status de destino desejado.
            new_status: Alias opcional para o status de destino.

        Returns:
            A instância atualizada de Contract.

        Raises:
            BusinessRuleViolation: Se a transição for inválida ou o status não for informado.
        """
        validate_tenant_ownership(
            company,
            instance,
            detail="Contrato não encontrado ou acesso negado.",
            code="contract_not_found_or_denied",
        )

        status_to_apply = target_status or new_status
        if not status_to_apply:
            raise BusinessRuleViolation(
                detail="Status de destino obrigatório.",
                code="missing_status",
            )

        instance.transition_to(status_to_apply)

        try:
            instance.save(update_fields=["status", "updated_at"])
        except ValidationError as e:
            msg = "; ".join(e.messages) if hasattr(e, "messages") else str(e)
            raise BusinessRuleViolation(
                detail=msg,
                code="contract_invalid_status_transition",
            ) from e

        return instance

    @staticmethod
    @transaction.atomic
    def send_to_pending(company: Company, instance: Contract) -> Contract:
        """Transita o contrato para pendente de assinaturas externas.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: Instância do contrato a ser transitada para pendente.

        Returns:
            A instância do Contract atualizada com status PENDING.

        Raises:
            BusinessRuleViolation: Se a transição de status for inválida.
        """
        validate_tenant_ownership(
            company,
            instance,
            detail="Contrato não encontrado ou acesso negado.",
            code="contract_not_found_or_denied",
        )
        instance.send_to_pending()
        try:
            instance.save(update_fields=["status", "updated_at"])
        except ValidationError as e:
            raise BusinessRuleViolation(
                detail="; ".join(e.messages) if hasattr(e, "messages") else str(e),
                code="contract_invalid_status_transition",
            ) from e
        return instance

    @staticmethod
    @transaction.atomic
    def cancel(company: Company, instance: Contract) -> Contract:
        """Cancela o contrato formalizado ou em negociação.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: Instância do contrato a ser cancelada.

        Returns:
            A instância do Contract atualizada com status CANCELED.

        Raises:
            BusinessRuleViolation: Se a transição de status for inválida.
        """
        validate_tenant_ownership(
            company,
            instance,
            detail="Contrato não encontrado ou acesso negado.",
            code="contract_not_found_or_denied",
        )
        instance.cancel()
        try:
            instance.save(update_fields=["status", "updated_at"])
        except ValidationError as e:
            raise BusinessRuleViolation(
                detail="; ".join(e.messages) if hasattr(e, "messages") else str(e),
                code="contract_invalid_status_transition",
            ) from e
        return instance

    @staticmethod
    @transaction.atomic
    def revert_to_draft(company: Company, instance: Contract) -> Contract:
        """Reverte o contrato para minuta.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: Instância do contrato a ser revertida para rascunho.

        Returns:
            A instância do Contract atualizada com status DRAFT.

        Raises:
            BusinessRuleViolation: Se a transição de status for inválida.
        """
        validate_tenant_ownership(
            company,
            instance,
            detail="Contrato não encontrado ou acesso negado.",
            code="contract_not_found_or_denied",
        )
        instance.revert_to_draft()
        try:
            instance.save(update_fields=["status", "updated_at"])
        except ValidationError as e:
            raise BusinessRuleViolation(
                detail="; ".join(e.messages) if hasattr(e, "messages") else str(e),
                code="contract_invalid_status_transition",
            ) from e
        return instance

    @staticmethod
    @transaction.atomic
    def attach_file(
        company: Company,
        instance: Contract,
        file: Any,
    ) -> Contract:
        """Anexa um arquivo ao contrato.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: Instância do contrato.
            file: Arquivo físico ou chave de armazenamento.

        Returns:
            Instância do Contract atualizada com o anexo.
        """
        validate_tenant_ownership(
            company,
            instance,
            detail="Contrato não encontrado ou acesso negado.",
            code="contract_not_found_or_denied",
        )
        instance.attach_file(file)
        instance.save(update_fields=["pdf_file", "updated_at"])
        return instance

    @staticmethod
    @transaction.atomic
    def detach_file(
        company: Company,
        instance: Contract,
    ) -> Contract:
        """Desanexa o arquivo do contrato caso não esteja assinado.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: Instância do contrato.

        Returns:
            Instância do Contract sem o arquivo anexo.
        """
        validate_tenant_ownership(
            company,
            instance,
            detail="Contrato não encontrado ou acesso negado.",
            code="contract_not_found_or_denied",
        )
        instance.detach_file()
        instance.save(update_fields=["pdf_file", "updated_at"])
        return instance

    @staticmethod
    def generate_upload_url(
        company: Company,
        wedding_id: Any = None,
        filename: Any = None,
        storage_service: StorageService | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Gera URL pré-assinada para upload de arquivo de contrato no Storage.

        Args:
            company: O tenant atual para isolamento de dados.
            wedding_id: Identificador único do casamento ou filename se posicional legado.
            filename: Nome do arquivo original ou wedding_id se posicional legado.
            storage_service: Instância opcional injetada de StorageService.
            kwargs: Parâmetros adicionais para compatibilidade.

        Returns:
            Dicionário com a URL pré-assinada e a chave do objeto.
        """
        raw_wedding_id = kwargs.get("wedding_id", wedding_id)
        raw_filename = kwargs.get("filename", filename)
        storage_svc = kwargs.get("storage_service", storage_service)

        if (
            isinstance(raw_wedding_id, str)
            and "." in raw_wedding_id
            and (
                isinstance(raw_filename, UUID)
                or (
                    isinstance(raw_filename, str)
                    and ("-" in raw_filename or raw_filename.isdigit())
                )
            )
        ):
            actual_wedding_id = raw_filename
            actual_filename = raw_wedding_id
        else:
            actual_wedding_id = raw_wedding_id
            actual_filename = raw_filename

        wedding = get_object_or_404_for_tenant(
            Wedding,
            company,
            actual_wedding_id,
            code="wedding_not_found_or_denied",
        )

        content_type = "application/pdf"
        ext = actual_filename.split(".")[-1].lower() if actual_filename else ""
        if ext in ["png", "jpg", "jpeg"]:
            content_type = f"image/{ext if ext != 'jpg' else 'jpeg'}"

        unique_id = uuid.uuid4()
        object_key = f"contracts/{wedding.uuid}/{unique_id}/{actual_filename}"

        r2_bucket = getattr(settings, "AWS_STORAGE_BUCKET_NAME", None) or getattr(
            settings, "R2_BUCKET", None
        )
        if not r2_bucket:
            logger.error("Configuração de storage R2/S3 incompleta no servidor.")
            raise BusinessRuleViolation(
                detail="Configuração de storage R2/S3 incompleta no servidor.",
                code="storage_configuration_incomplete",
            )

        storage = storage_svc or ContractService.get_storage_client()
        upload_url = storage.generate_presigned_put_url(
            bucket=r2_bucket,
            object_key=object_key,
            content_type=content_type,
            expires_in=900,
        )
        return {"upload_url": upload_url, "object_key": object_key}

    @staticmethod
    @transaction.atomic
    def upload_file(
        company: Company,
        instance: Contract | UUID | str | None = None,
        pdf_file_key: str = "",
        *,
        uuid: UUID | str | None = None,
    ) -> Contract:
        """Associa a chave do arquivo no storage ao contrato.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: Instância do contrato ou UUID se posicional legado.
            pdf_file_key: Chave do arquivo persistido no storage.
            uuid: Identificador do contrato caso instance não seja informado.

        Returns:
            Instância do Contract atualizada.
        """
        target: Contract
        target_uuid = uuid
        if isinstance(instance, (str, UUID)):
            target_uuid = instance
            instance = None

        if instance is not None:
            validate_tenant_ownership(
                company,
                instance,
                detail="Contrato não encontrado ou acesso negado.",
                code="contract_not_found_or_denied",
            )
            target = instance
        elif target_uuid is not None:
            target = contract_get_selector(company, target_uuid)
        else:
            raise BusinessRuleViolation(
                detail="Contrato não informado para upload.",
                code="missing_contract",
            )

        target.pdf_file = pdf_file_key
        target.save(update_fields=["pdf_file", "updated_at"])
        return target

    @staticmethod
    @transaction.atomic
    def delete_file(company: Company, uuid: UUID | str) -> None:
        """Remove a associação de arquivo físico do contrato.

        Args:
            company: O tenant atual para isolamento de dados.
            uuid: Identificador único (UUID ou string) do contrato.
        """
        logger.info("Removendo arquivo do contrato uuid=%s", uuid)
        contract = contract_get_selector(company, uuid)
        contract.detach_file()
        contract.save(update_fields=["pdf_file", "updated_at"])
        logger.info("Arquivo removido do contrato uuid=%s", uuid)
