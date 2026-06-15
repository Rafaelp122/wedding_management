from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any
from uuid import UUID

from django.conf import settings
from django.db import transaction
from django.db.models import (
    Count,
    F,
    OuterRef,
    ProtectedError,
    QuerySet,
    Subquery,
    Sum,
    Value,
)
from django.db.models.functions import Coalesce

from apps.core.exceptions import (
    BusinessRuleViolation,
    DomainIntegrityError,
    ObjectNotFoundError,
)
from apps.finances.models import Expense, Installment
from apps.finances.services.expense_service import ExpenseService
from apps.logistics.models import Contract, Supplier
from apps.logistics.services.item_service import ItemService
from apps.tenants.models import Company
from apps.weddings.models import Wedding


logger = logging.getLogger(__name__)

# Aliases para evitar colisão do método 'list'
# com o built-in 'list' no escopo da classe
_ListDict = list[dict[str, Any]]
_ListStr = list[str]


class ContractService:
    """
    Camada de serviço para gestão de contratos.
    Foco: Orquestração, Multitenancy Segura e Auditoria.
    Validações de integridade do dado (ex: datas inválidas) ficam delegadas ao Model.
    """

    @staticmethod
    def list(
        company: Company,
        wedding_id: UUID | str | None = None,
        status: str | None = None,
        supplier_id: UUID | str | None = None,
    ) -> QuerySet[Contract]:
        qs = (
            Contract.objects.for_tenant(company)
            .select_related("supplier", "wedding", "parent")
            .annotate(
                supplier_name=F("supplier__name"),
                supplier_phone=F("supplier__phone"),
                supplier_email=F("supplier__email"),
                expense_id=Subquery(
                    Expense.objects.filter(contract=OuterRef("pk")).values("uuid")[:1]
                ),
                total_paid=Coalesce(
                    Subquery(
                        Installment.objects.filter(
                            expense__contract=OuterRef("pk"), status="PAID"
                        )
                        .values("expense__contract")
                        .annotate(s=Sum("amount"))
                        .values("s")[:1]
                    ),
                    Value(Decimal("0.00")),
                ),
                addendums_count=Count("addendums"),
            )
        )
        if wedding_id:
            qs = qs.filter(wedding__uuid=wedding_id)
        if status:
            qs = qs.filter(status=status)
        if supplier_id:
            qs = qs.filter(supplier__uuid=supplier_id)
        return qs

    @staticmethod
    def get(company: Company, uuid: UUID | str) -> Contract:
        try:
            return (
                Contract.objects.for_tenant(company)
                .select_related("supplier", "wedding", "parent")
                .annotate(
                    addendums_count=Count("addendums"),
                    expense_id=Subquery(
                        Expense.objects.filter(contract=OuterRef("pk")).values("uuid")[
                            :1
                        ]
                    ),
                )
                .get(uuid=uuid)
            )
        except Contract.DoesNotExist as e:
            raise ObjectNotFoundError(detail="Contrato não encontrado.") from e

    @staticmethod
    @transaction.atomic
    def create(company: Company, data: dict[str, Any]) -> Contract:
        logger.info(f"Iniciando criação de Contrato para company_id={company.id}")

        # 1. Resolução Segura de Dependências (Suporta Instância ou UUID)
        wedding_input = data.pop("wedding", None)
        supplier_input = data.pop("supplier", None)
        pdf_file_key = data.pop("pdf_file_key", None)

        # Resolução do Casamento
        if isinstance(wedding_input, Wedding):
            wedding = wedding_input
        else:
            try:
                wedding = Wedding.objects.for_tenant(company).get(uuid=wedding_input)
            except Wedding.DoesNotExist as e:
                logger.warning(
                    f"Tentativa de uso de casamento inválido/negado: {wedding_input}"
                )
                raise ObjectNotFoundError(
                    detail="Casamento não encontrado ou acesso negado.",
                    code="wedding_not_found_or_denied",
                ) from e

        # Resolução do Fornecedor
        if isinstance(supplier_input, Supplier):
            supplier = supplier_input
        else:
            try:
                supplier = Supplier.objects.for_tenant(company).get(uuid=supplier_input)
            except Supplier.DoesNotExist as e:
                logger.warning(
                    f"Tentativa de uso de fornecedor inválido/negado: {supplier_input}"
                )
                raise ObjectNotFoundError(
                    detail="Fornecedor não encontrado ou acesso negado.",
                    code="supplier_not_found_or_denied",
                ) from e

        parent_input = data.pop("parent", None)
        parent = None
        if parent_input:
            try:
                parent = Contract.objects.for_tenant(company).get(uuid=parent_input)
            except Contract.DoesNotExist as e:
                raise ObjectNotFoundError(
                    detail="Contrato pai não encontrado.",
                    code="parent_contract_not_found",
                ) from e

        # 2. Instanciação em Memória
        contract = Contract(
            company=company,
            wedding=wedding,
            supplier=supplier,
            parent=parent,
            pdf_file=pdf_file_key,
            **data,
        )

        # 3. Validação Estrita (O Model aplica as suas regras, incluindo checagem de
        # datas)
        contract.save()

        logger.info(f"Contrato criado com sucesso: uuid={contract.uuid}")
        return contract

    @staticmethod
    @transaction.atomic
    def create_full(
        company: Company,
        *,
        contract_data: dict[str, Any],
        items_data: _ListDict | None = None,
        expense_data: dict[str, Any] | None = None,
        pdf_file_key: str | None = None,
    ) -> Contract:
        """
        Orquestra a criação completa de um contrato.
        Cria o contrato base, associa opcionalmente a chave do arquivo PDF/imagem
        do R2/S3,
        cria os itens logísticos associados e inicializa o fluxo de despesa
        financeira correspondente.
        Em caso de falha em qualquer etapa, garante o rollback no banco.
        """
        logger.info(
            f"Iniciando criação completa de Contrato para company_id={company.id}"
        )

        contract = ContractService.create(company=company, data=contract_data)

        if pdf_file_key:
            contract.pdf_file = pdf_file_key
            contract.save(update_fields=["pdf_file"])

        if items_data:
            for item_dict in items_data:
                item_dict["wedding"] = contract.wedding
                item_dict["contract"] = contract
                ItemService.create(company=company, data=item_dict)

        if expense_data:
            expense_data["contract"] = contract
            ExpenseService.create(company=company, data=expense_data)

        logger.info(f"Criação completa de Contrato finalizada: uuid={contract.uuid}")
        return contract

    @staticmethod
    def _resolve_parent(
        company: Company, instance: Contract, parent_input: Any
    ) -> None:
        parent: Contract | None = None
        if isinstance(parent_input, Contract):
            parent = parent_input
        elif parent_input == "":
            instance.parent = None
            return
        else:
            try:
                parent = Contract.objects.for_tenant(company).get(uuid=parent_input)
            except Contract.DoesNotExist as e:
                raise ObjectNotFoundError(
                    detail="Contrato pai inválido ou acesso negado.",
                    code="parent_contract_not_found_or_denied",
                ) from e

        if parent is not None:
            if parent.pk == instance.pk:
                raise BusinessRuleViolation(
                    detail="Um contrato não pode ser pai de si mesmo.",
                    code="contract_self_parent",
                )
            if parent.wedding_id != instance.wedding_id:
                raise BusinessRuleViolation(
                    detail="O contrato pai deve pertencer ao mesmo casamento.",
                    code="contract_cross_wedding_parent",
                )
            # Prevent circular: parent can't be a descendant of instance
            current = parent
            while current.parent:
                if current.parent.pk == instance.pk:
                    raise BusinessRuleViolation(
                        detail="Não é possível vincular um contrato pai que é "
                        "descendente deste contrato.",
                        code="contract_circular_parent",
                    )
                current = current.parent
            instance.parent = parent

    @staticmethod
    @transaction.atomic
    def update(company: Company, instance: Contract, data: dict[str, Any]) -> Contract:
        logger.info(
            f"Atualizando Contrato uuid={instance.uuid} por company_id={company.id}"
        )

        data.pop("wedding", None)
        data.pop("company", None)
        pdf_file_key = data.pop("pdf_file_key", None)
        if pdf_file_key is not None:
            instance.pdf_file = pdf_file_key

        supplier_input = data.pop("supplier", None)
        if supplier_input:
            if isinstance(supplier_input, Supplier):
                instance.supplier = supplier_input
            else:
                try:
                    instance.supplier = Supplier.objects.for_tenant(company).get(
                        uuid=supplier_input
                    )
                except Supplier.DoesNotExist as e:
                    raise ObjectNotFoundError(
                        detail="Fornecedor inválido ou acesso negado.",
                        code="supplier_not_found_or_denied",
                    ) from e

        parent_input = data.pop("parent", None)
        if parent_input is not None:
            ContractService._resolve_parent(company, instance, parent_input)

        status_input = data.pop("status", None)
        if status_input is not None and status_input != instance.status:
            ContractService.transition_status(company, instance, status_input)

        for field, value in data.items():
            if field == "pdf_file" and value is None:
                continue
            setattr(instance, field, value)

        instance.save()

        logger.info(f"Contrato uuid={instance.uuid} atualizado com sucesso.")
        return instance

    @staticmethod
    @transaction.atomic
    def delete(company: Company, instance: Contract) -> None:
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
        logger.info(
            f"Transição de status do Contrato uuid={instance.uuid}: "
            f"{instance.status} -> {new_status}"
        )

        if instance.company_id != company.id:
            raise ObjectNotFoundError(detail="Contrato não encontrado.")

        # TODO(sprint/018): mover máquina de estados para Contract.clean()
        allowed_transitions: dict[str, _ListStr] = {
            "DRAFT": ["PENDING", "CANCELED"],
            "PENDING": ["SIGNED", "DRAFT", "CANCELED"],
            "SIGNED": ["CANCELED"],
            "CANCELED": ["DRAFT"],
        }

        current = instance.status
        allowed = allowed_transitions.get(current, [])

        if new_status not in allowed:
            raise BusinessRuleViolation(
                detail=f"Não é permitido transitar de '{current}' para '{new_status}'.",
                code="contract_invalid_status_transition",
            )

        instance.status = new_status
        instance.save()

        logger.info(f"Contrato uuid={instance.uuid} transitado para '{new_status}'.")
        return instance

    @staticmethod
    @transaction.atomic
    def upload_file(company: Company, uuid: UUID | str, pdf_file_key: str) -> Contract:
        """
        Associa a chave do arquivo (pdf_file_key) carregado no R2/S3 ao contrato.
        """
        logger.info(
            f"Associando chave de arquivo {pdf_file_key} ao contrato uuid={uuid}"
        )
        contract = ContractService.get(company, uuid)
        contract.pdf_file = pdf_file_key
        contract.save(update_fields=["pdf_file"])
        logger.info(f"Chave de arquivo associada ao contrato uuid={uuid}")
        return contract

    @staticmethod
    def delete_file(company: Company, uuid: UUID | str) -> None:
        """
        Remove o arquivo vinculado ao contrato.
        """
        logger.info(f"Removendo arquivo do contrato uuid={uuid}")
        contract = ContractService.get(company, uuid)
        if contract.pdf_file:
            contract.pdf_file.delete(save=False)
        contract.pdf_file = None
        contract.save(update_fields=["pdf_file"])
        logger.info(f"Arquivo removido do contrato uuid={uuid}")

    @staticmethod
    def generate_upload_url(
        company: Company, filename: str, wedding_id: UUID | str
    ) -> dict[str, Any]:
        """
        Gera presigned URL para upload de contrato no R2/S3.
        """
        import uuid

        import boto3  # type: ignore[import-untyped]

        # Validar casamento
        try:
            wedding = Wedding.objects.for_tenant(company).get(uuid=wedding_id)
        except Wedding.DoesNotExist as e:
            logger.warning(
                f"Tentativa de gerar upload URL para casamento inválido: {wedding_id}"
            )
            raise ObjectNotFoundError(
                detail="Casamento não encontrado ou acesso negado.",
                code="wedding_not_found_or_denied",
            ) from e

        # Determinar Content-Type com base no filename
        content_type = "application/pdf"
        ext = filename.split(".")[-1].lower()
        if ext in ["png", "jpg", "jpeg"]:
            content_type = f"image/{ext if ext != 'jpg' else 'jpeg'}"

        # Gerar chave única
        unique_id = uuid.uuid4()
        object_key = f"contracts/{wedding.uuid}/{unique_id}/{filename}"

        # Configurar boto3 client
        r2_endpoint = getattr(settings, "AWS_S3_ENDPOINT_URL", None) or getattr(
            settings, "R2_ENDPOINT_URL", None
        )
        r2_access_key = getattr(settings, "AWS_ACCESS_KEY_ID", None) or getattr(
            settings, "R2_ACCESS_KEY_ID", None
        )
        r2_secret_key = getattr(settings, "AWS_SECRET_ACCESS_KEY", None) or getattr(
            settings, "R2_SECRET_ACCESS_KEY", None
        )
        r2_bucket = getattr(settings, "AWS_STORAGE_BUCKET_NAME", None) or getattr(
            settings, "R2_BUCKET", None
        )

        if not all([r2_endpoint, r2_access_key, r2_secret_key, r2_bucket]):
            logger.error("Configuração de storage R2/S3 incompleta no servidor.")
            raise BusinessRuleViolation(
                detail="Configuração de storage R2/S3 incompleta no servidor.",
                code="storage_configuration_incomplete",
            )

        s3_client = boto3.client(
            "s3",
            endpoint_url=r2_endpoint,
            aws_access_key_id=r2_access_key,
            aws_secret_access_key=r2_secret_key,
            region_name=getattr(settings, "AWS_S3_REGION_NAME", "us-east-1"),
        )

        presigned_url = s3_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": r2_bucket,
                "Key": object_key,
                "ContentType": content_type,
            },
            ExpiresIn=900,
        )

        return {
            "upload_url": presigned_url,
            "object_key": object_key,
        }
