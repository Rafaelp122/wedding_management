from __future__ import annotations

import json
import logging
from datetime import date
from typing import Any
from uuid import UUID

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import ProtectedError
from pydantic import ValidationError as PydanticValidationError

from apps.core.exceptions import (
    BusinessRuleViolation,
    DomainIntegrityError,
)
from apps.core.services.storage import (
    StorageService,
    get_storage_service,
)
from apps.core.shortcuts import get_object_or_404_for_tenant, resolve_tenant_resource
from apps.core.tenant import validate_tenant_ownership
from apps.finances.interfaces import ExpenseIn, create_expense_from_contract
from apps.logistics.models import Contract, Supplier
from apps.logistics.schemas import (
    ContractFullCreateIn,
    ContractIn,
    ContractPatchIn,
    ItemIn,
)
from apps.logistics.selectors.contract_selectors import contract_get_selector
from apps.logistics.services.item_service import ItemService
from apps.tenants.models import Company
from apps.weddings.models import Wedding


_ItemInList = list[ItemIn]

logger = logging.getLogger(__name__)


class ContractService:
    """
    Camada de serviço para gestão de contratos.
    Foco: Orquestração de escrita, Multitenancy Segura e Auditoria.
    Validações de integridade do dado ficam delegadas ao Model.
    """

    # Injeção de dependência para desacoplar a infraestrutura de Storage (R2/S3).
    # Permite que testes unitários injetem mocks para evitar chamadas de rede e
    # dependências de configurações reais de ambiente.
    _storage_service: StorageService | None = None

    @classmethod
    def get_storage_client(cls) -> StorageService:
        """
        Retorna o cliente de storage ativo.

        Se nenhuma dependência foi injetada anteriormente, inicializa a
        implementação padrão obtida a partir do app core.

        Returns:
            A instância ativa de StorageService.
        """
        if cls._storage_service is None:
            cls._storage_service = get_storage_service()
        return cls._storage_service

    @classmethod
    def set_storage_service(cls, storage_service: StorageService) -> None:
        """
        Injeta uma instância de StorageService.

        Utilizado para fins de testes ou substituição de infraestrutura
        em runtime.

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
        """
        Cria um contrato completo a partir do payload HTTP.

        Centraliza a montagem dos DTOs de contrato, itens e despesa para manter a
        rota responsável apenas por autenticação e delegação.

        Args:
            company: O tenant atual para isolamento de dados.
            payload: Dados validados pelo schema da rota de criação completa.

        Returns:
            A instância do Contract criada e totalmente populada.
        """
        contract_data = ContractIn(
            wedding=payload.wedding,
            supplier=payload.supplier,
            name=payload.name,
            total_amount=payload.total_amount,
            status=payload.status,
            description=payload.description,
            parent=payload.parent,
        )

        items_data = ContractService._build_full_items_payload(payload)
        expense_data = ContractService._build_full_expense_payload(payload)

        return ContractService.create_full(
            company=company,
            contract_data=contract_data,
            items_data=items_data,
            expense_data=expense_data,
            pdf_file_key=payload.pdf_file_key,
        )

    @staticmethod
    def _build_full_items_payload(
        payload: ContractFullCreateIn,
    ) -> _ItemInList | None:
        """
        Converte o JSON de itens do payload completo em schemas de criação.

        Args:
            payload: Dados recebidos pelo endpoint de criação completa.

        Returns:
            Lista de itens normalizada com o casamento do contrato ou None.

        Raises:
            BusinessRuleViolation: Se `items_data` não for uma lista de objetos
                JSON compatíveis com ItemIn.
        """
        try:
            raw_items = json.loads(payload.items_data or "[]")
        except json.JSONDecodeError as e:
            raise BusinessRuleViolation(
                detail="items_data deve ser um JSON válido.",
                code="invalid_items_data",
            ) from e

        if not isinstance(raw_items, list) or not all(
            isinstance(item_data, dict) for item_data in raw_items
        ):
            raise BusinessRuleViolation(
                detail="items_data deve ser uma lista de objetos JSON.",
                code="invalid_items_data",
            )

        try:
            items_data = [
                ItemIn(**{**item_data, "wedding": payload.wedding})
                for item_data in raw_items
            ]
        except PydanticValidationError as e:
            raise BusinessRuleViolation(
                detail="items_data contém item inválido.",
                code="invalid_items_data",
            ) from e
        return items_data or None

    @staticmethod
    def _build_full_expense_payload(
        payload: ContractFullCreateIn,
    ) -> ExpenseIn | None:
        """
        Monta o payload financeiro opcional para criação completa de contrato.

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
        """
        Cria um contrato básico no banco de dados.

        Resolve as chaves estrangeiras de casamento, fornecedor e
        contrato pai correspondentes ao tenant informado.

        Args:
            company: O tenant atual para isolamento de dados.
            payload: Objeto de entrada contendo os dados do contrato.

        Returns:
            A instância criada do Contract.

        Raises:
            ObjectNotFoundError: Se algum objeto relacionado (casamento, fornecedor
                ou contrato pai) não for encontrado para o tenant.
        """
        logger.info(f"Iniciando criação de Contrato para company_id={company.id}")

        data = payload.model_dump(exclude_unset=True)

        wedding_input = data.pop("wedding", None)
        supplier_input = data.pop("supplier", None)
        pdf_file_key = data.pop("pdf_file_key", None)

        wedding = resolve_tenant_resource(
            Wedding,
            company,
            wedding_input,
            detail="Casamento não encontrado ou acesso negado.",
            code="wedding_not_found_or_denied",
        )

        supplier = resolve_tenant_resource(
            Supplier,
            company,
            supplier_input,
            detail="Fornecedor inválido ou acesso negado.",
            code="supplier_not_found_or_denied",
        )

        parent_input = data.pop("parent", None)
        parent = None
        if parent_input:
            parent = resolve_tenant_resource(
                Contract,
                company,
                parent_input,
                detail="Contrato pai não encontrado.",
                code="parent_contract_not_found",
            )

        # 2. Instanciação em Memória
        contract = Contract(
            company=company,
            wedding=wedding,
            supplier=supplier,
            pdf_file=pdf_file_key,
            **data,
        )
        if parent:
            contract.set_parent(parent)

        # 3. Persistência
        try:
            contract.save()
        except ValidationError as e:
            msg = "; ".join(e.messages) if hasattr(e, "messages") else str(e)
            raise BusinessRuleViolation(
                detail=msg,
                code="contract_creation_validation_error",
            ) from e

        logger.info(f"Contrato criado com sucesso: uuid={contract.uuid}")
        return contract

    @staticmethod
    @transaction.atomic
    def create_full(
        company: Company,
        *,
        contract_data: ContractIn,
        items_data: _ItemInList | None = None,
        expense_data: ExpenseIn | None = None,
        pdf_file_key: str | None = None,
    ) -> Contract:
        """
        Orquestra a criação completa de um contrato.

        Cria o contrato básico, anexa o PDF/imagem e, opcionalmente,
        cria itens logísticos e a despesa correspondente. Se qualquer
        etapa falhar, o rollback é efetuado.

        Args:
            company: O tenant atual para isolamento de dados.
            contract_data: Dados básicos do contrato.
            items_data: Lista opcional de itens a serem criados.
            expense_data: Dados opcionais da despesa para parcelamento.
            pdf_file_key: Chave do arquivo PDF/imagem salvo no storage.

        Returns:
            A instância do Contract criada e totalmente populada.
        """
        contract = ContractService.create(company=company, payload=contract_data)

        if pdf_file_key:
            contract.attach_file(pdf_file_key)
            contract.save(update_fields=["pdf_file", "updated_at"])

        if items_data:
            for item in items_data:
                ItemService.create(
                    company=company,
                    payload=item.model_copy(
                        update={
                            "wedding": contract.wedding.uuid,
                            "contract": contract.uuid,
                        }
                    ),
                )

        if expense_data:
            expense = create_expense_from_contract(
                company=company,
                payload=expense_data,
                contract_uuid=contract.uuid,
            )
            # Otimização: Popula o cache reverso OneToOne para serialização imediata.
            contract.expense = expense

        logger.info(f"Criação completa de Contrato finalizada: uuid={contract.uuid}")
        return contract

    @staticmethod
    def _resolve_parent(
        company: Company, instance: Contract, parent_input: Any
    ) -> None:
        """
        Resolve o contrato pai e valida regras de hierarquia de contratos.

        Regra de Negócio:
            BR-L02-A a BR-L02-C:
            docs/architecture/business-rules/logistics/contract-parent-child-hierarchy.md
        Decisão Arquitetural:
            ADR-030 (docs/architecture/adr/030-rich-domain-model-service-layer.md)

        Args:
            company: O tenant atual para isolamento de dados.
            instance: O contrato em edição que receberá o pai.
            parent_input: Instância, UUID, string do contrato pai,
                ou string vazia para remover vínculo.

        Raises:
            BusinessRuleViolation: Se houver tentativa de auto-vínculo,
                casamentos divergentes ou vinculação cíclica.
            ObjectNotFoundError: Se o contrato pai não for encontrado para o tenant.
        """
        if parent_input == "":
            instance.remove_parent()
            return

        parent = resolve_tenant_resource(
            Contract,
            company,
            parent_input,
            detail="Contrato pai inválido ou acesso negado.",
            code="parent_contract_not_found_or_denied",
        )
        instance.set_parent(parent)

    @staticmethod
    @transaction.atomic
    def update(
        company: Company, instance: Contract, payload: ContractPatchIn
    ) -> Contract:
        """
        Atualiza dados de um contrato do tenant.

        Garante a validação de acesso ao tenant, além de resolver as
        referências de fornecedor, contrato pai e status.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: A instância do Contract a ser atualizada.
            payload: Dados de alteração parcial para atualização.

        Returns:
            A instância de Contract atualizada.

        Raises:
            BusinessRuleViolation: Se a validação dos dados falhar.
            ObjectNotFoundError: Se o contrato ou relacionados não forem encontrados
                para o tenant.
        """
        validate_tenant_ownership(
            company,
            instance,
            detail="Contrato não encontrado ou acesso negado.",
            code="contract_not_found_or_denied",
        )
        logger.info(
            f"Atualizando Contrato uuid={instance.uuid} por company_id={company.id}"
        )

        updated_fields: set[str] = set()

        data = payload.model_dump(exclude_unset=True)
        pdf_file_key = data.pop("pdf_file_key", None)
        if pdf_file_key is not None:
            instance.attach_file(pdf_file_key)
            updated_fields.add("pdf_file")

        supplier_input = data.pop("supplier", None)
        if supplier_input:
            instance.supplier = resolve_tenant_resource(
                Supplier,
                company,
                supplier_input,
                detail="Fornecedor inválido ou acesso negado.",
                code="supplier_not_found_or_denied",
            )
            updated_fields.add("supplier")

        parent_input = data.pop("parent", None)
        if parent_input is not None:
            ContractService._resolve_parent(company, instance, parent_input)
            updated_fields.add("parent")

        status_input = data.pop("status", None)
        if status_input is not None and status_input != instance.status:
            instance.transition_to(status_input)
            updated_fields.add("status")

        ContractService._apply_fields(instance, data, updated_fields)

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

        logger.info(f"Contrato uuid={instance.uuid} atualizado com sucesso.")
        return instance

    @staticmethod
    def _apply_fields(
        instance: Contract, data: dict[str, Any], updated_fields: set[str]
    ) -> None:
        """
        Aplica campos simples de dicionário na instância do contrato.

        Ignora o campo de arquivo caso seja explicitamente None.

        Args:
            instance: A instância de Contract que receberá as alterações.
            data: Dicionário mapeando os campos do model a valores.
            updated_fields: Conjunto de campos atualizados para rastreamento.
        """
        for field, value in data.items():
            if field == "pdf_file" and value is None:
                continue
            setattr(instance, field, value)
            updated_fields.add(field)

    @staticmethod
    @transaction.atomic
    def delete(company: Company, instance: Contract) -> None:
        """
        Remove um contrato e suas dependências físicas.

        Desvincula os itens logísticos órfãos e remove o arquivo físico.
        Valida a propriedade do tenant antes de excluir.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: A instância do Contract a ser removida.

        Raises:
            DomainIntegrityError: Se houverem aditivos vinculados.
            ObjectNotFoundError: Se o contrato não pertencer ao tenant.
        """
        validate_tenant_ownership(
            company,
            instance,
            detail="Contrato não encontrado ou acesso negado.",
            code="contract_not_found_or_denied",
        )
        logger.info(
            f"Tentativa de deleção do Contrato uuid={instance.uuid} por "
            f"company_id={company.id}"
        )

        # Desvinculação de itens logísticos órfãos
        instance.items.update(contract=None)

        # Remover arquivo físico se houver
        if instance.pdf_file:
            instance.pdf_file.delete(save=False)

        try:
            instance.delete()
            logger.warning(
                f"Contrato uuid={instance.uuid} DESTRUÍDO por company_id={company.id}"
            )
        except ProtectedError as e:
            raise DomainIntegrityError(
                detail="Não é possível apagar este contrato pois existem "
                "aditivos vinculados a ele. Remova os aditivos primeiro.",
                code="contract_protected_by_addendums",
            ) from e

    @staticmethod
    @transaction.atomic
    def transition_status(
        company: Company, instance: Contract, new_status: str
    ) -> Contract:
        """
        Executa a transição de status do contrato.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: A instância do Contract a ter o status alterado.
            new_status: O novo status desejado para o contrato.

        Returns:
            A instância atualizada de Contract.

        Raises:
            BusinessRuleViolation: Se a transição for inválida.
            ObjectNotFoundError: Se o contrato não pertencer ao tenant.
        """
        logger.info(
            f"Transição de status do Contrato uuid={instance.uuid}: "
            f"{instance.status} -> {new_status}"
        )

        validate_tenant_ownership(
            company,
            instance,
            detail="Contrato não encontrado ou acesso negado.",
            code="contract_not_found_or_denied",
        )

        instance.transition_to(new_status)
        try:
            instance.save(update_fields=["status", "updated_at"])
        except ValidationError as e:
            raise BusinessRuleViolation(
                detail="; ".join(e.messages),
                code="contract_invalid_status_transition",
            ) from e

        logger.info(f"Contrato uuid={instance.uuid} transitado para '{new_status}'.")
        return instance

    @staticmethod
    @transaction.atomic
    def send_to_pending(company: Company, instance: Contract) -> Contract:
        """Transita o contrato para pendente de assinaturas externas.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: A instância do Contract a ter o status alterado.

        Returns:
            A instância atualizada de Contract.

        Raises:
            BusinessRuleViolation: Se a transição for inválida.
            ObjectNotFoundError: Se o contrato não pertencer ao tenant.
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
    def sign(
        company: Company,
        instance: Contract,
        *,
        signed_date: date | None = None,
        pdf_file_key: str | None = None,
    ) -> Contract:
        """Formaliza a assinatura do contrato externamente.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: A instância do Contract a ser assinada.
            signed_date: Data opcional em que o contrato foi assinado.
            pdf_file_key: Chave opcional do arquivo PDF no storage.

        Returns:
            A instância atualizada de Contract.

        Raises:
            BusinessRuleViolation: Se a transição for inválida ou campos
                obrigatórios faltarem.
            ObjectNotFoundError: Se o contrato não pertencer ao tenant.
        """
        validate_tenant_ownership(
            company,
            instance,
            detail="Contrato não encontrado ou acesso negado.",
            code="contract_not_found_or_denied",
        )
        instance.sign(signed_date=signed_date, pdf_file=pdf_file_key)
        updated_fields = {"status", "updated_at"}
        if signed_date is not None:
            updated_fields.add("signed_date")
        if pdf_file_key is not None:
            updated_fields.add("pdf_file")

        try:
            instance.save(update_fields=list(updated_fields))
        except ValidationError as e:
            raise BusinessRuleViolation(
                detail="; ".join(e.messages) if hasattr(e, "messages") else str(e),
                code="contract_invalid_status_transition",
            ) from e
        return instance

    @staticmethod
    @transaction.atomic
    def cancel(company: Company, instance: Contract) -> Contract:
        """Cancela o contrato.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: A instância do Contract a ser cancelada.

        Returns:
            A instância atualizada de Contract.

        Raises:
            BusinessRuleViolation: Se a transição for inválida.
            ObjectNotFoundError: Se o contrato não pertencer ao tenant.
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
        """Reverte o contrato para o estado de rascunho.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: A instância do Contract a ser revertida.

        Returns:
            A instância atualizada de Contract.

        Raises:
            BusinessRuleViolation: Se a transição for inválida.
            ObjectNotFoundError: Se o contrato não pertencer ao tenant.
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
    def upload_file(company: Company, uuid: UUID | str, pdf_file_key: str) -> Contract:
        """
        Associa uma chave de arquivo já carregada no storage ao contrato.

        Args:
            company: O tenant atual para isolamento de dados.
            uuid: Identificador único (UUID ou string) do contrato.
            pdf_file_key: A chave do objeto de arquivo salva no storage.

        Returns:
            A instância atualizada de Contract.

        Raises:
            ObjectNotFoundError: Se o contrato não for encontrado para o tenant.
        """
        logger.info(
            f"Associando chave de arquivo {pdf_file_key} ao contrato uuid={uuid}"
        )
        contract = contract_get_selector(company, uuid)
        contract.pdf_file = pdf_file_key
        contract.save(update_fields=["pdf_file", "updated_at"])
        logger.info(f"Chave de arquivo associada ao contrato uuid={uuid}")
        return contract

    @staticmethod
    @transaction.atomic
    def delete_file(company: Company, uuid: UUID | str) -> None:
        """
        Remove a associação de arquivo físico do contrato.

        Deleta o arquivo físico do storage caso exista.

        Args:
            company: O tenant atual para isolamento de dados.
            uuid: Identificador único (UUID ou string) do contrato.

        Raises:
            ObjectNotFoundError: Se o contrato não for encontrado para o tenant.
        """
        logger.info(f"Removendo arquivo do contrato uuid={uuid}")
        contract = contract_get_selector(company, uuid)
        contract.detach_file()
        contract.save(update_fields=["pdf_file", "updated_at"])
        logger.info(f"Arquivo removido do contrato uuid={uuid}")

    @staticmethod
    def generate_upload_url(
        company: Company,
        filename: str,
        wedding_id: UUID | str,
        storage_service: StorageService | None = None,
    ) -> dict[str, Any]:
        """
        Gera presigned URL para upload direto de contrato no R2/S3.

        Args:
            company: O tenant atual para isolamento de dados.
            filename: Nome do arquivo original a ser carregado.
            wedding_id: Identificador único do casamento associado.
            storage_service: Serviço de storage opcional para injeção.

        Returns:
            Dicionário contendo a 'upload_url' e a 'object_key'.

        Raises:
            BusinessRuleViolation: Se a configuração do storage
                estiver incompleta no servidor.
            ObjectNotFoundError: Se o casamento não for encontrado para o tenant.
        """
        import uuid

        # Validar casamento
        wedding = get_object_or_404_for_tenant(
            Wedding,
            company,
            wedding_id,
            code="wedding_not_found_or_denied",
        )

        # Determinar Content-Type com base no filename
        content_type = "application/pdf"
        ext = filename.split(".")[-1].lower()
        if ext in ["png", "jpg", "jpeg"]:
            content_type = f"image/{ext if ext != 'jpg' else 'jpeg'}"

        # Gerar chave única
        unique_id = uuid.uuid4()
        object_key = f"contracts/{wedding.uuid}/{unique_id}/{filename}"

        # Obter bucket das configurações
        r2_bucket = getattr(settings, "AWS_STORAGE_BUCKET_NAME", None) or getattr(
            settings, "R2_BUCKET", None
        )

        if not r2_bucket:
            logger.error("Configuração de storage R2/S3 incompleta no servidor.")
            raise BusinessRuleViolation(
                detail="Configuração de storage R2/S3 incompleta no servidor.",
                code="storage_configuration_incomplete",
            )

        storage = storage_service or ContractService.get_storage_client()
        presigned_url = storage.generate_presigned_put_url(
            bucket=r2_bucket,
            object_key=object_key,
            content_type=content_type,
            expires_in=900,
        )

        return {
            "upload_url": presigned_url,
            "object_key": object_key,
        }
