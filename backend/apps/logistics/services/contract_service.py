from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any
from uuid import UUID

from django.conf import settings
from django.core.exceptions import ValidationError
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
from apps.core.shortcuts import get_object_or_404_for_tenant
from apps.core.tenant import validate_tenant_ownership
from apps.finances.models import Expense, Installment
from apps.finances.schemas import ExpenseIn
from apps.finances.services.expense_service import ExpenseService
from apps.logistics.models import Contract, Supplier
from apps.logistics.schemas import ContractIn, ContractPatchIn, ItemIn
from apps.logistics.services.item_service import ItemService
from apps.tenants.models import Company
from apps.weddings.models import Wedding


_ItemInList = list[ItemIn]


logger = logging.getLogger(__name__)


# Aliases para evitar colisão do método 'list'
# com o built-in 'list' no escopo da classe
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
        parent_id: UUID | str | None = None,
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
                # Bolt Optimization: Use Subquery for count to avoid join explosion
                addendums_count=Coalesce(
                    Subquery(
                        Contract.objects.filter(parent=OuterRef("pk"))
                        .values("parent")
                        .annotate(cnt=Count("id"))
                        .values("cnt")[:1]
                    ),
                    0,
                ),
            )
        )
        if wedding_id:
            qs = qs.filter(wedding__uuid=wedding_id)
        if status:
            qs = qs.filter(status=status)
        if supplier_id:
            qs = qs.filter(supplier__uuid=supplier_id)
        if parent_id:
            qs = qs.filter(parent__uuid=parent_id)
        return qs

    @staticmethod
    def get(company: Company, uuid: UUID | str) -> Contract:
        """Busca um contrato com annotations detalhadas."""
        try:
            return (
                Contract.objects.for_tenant(company)
                .select_related("supplier", "wedding", "parent")
                .annotate(
                    # Bolt Optimization: Use Subquery for count to avoid join explosion
                    addendums_count=Coalesce(
                        Subquery(
                            Contract.objects.filter(parent=OuterRef("pk"))
                            .values("parent")
                            .annotate(cnt=Count("id"))
                            .values("cnt")[:1]
                        ),
                        0,
                    ),
                    expense_id=Subquery(
                        Expense.objects.filter(contract=OuterRef("pk")).values("uuid")[
                            :1
                        ]
                    ),
                )
                .get(uuid=uuid)
            )
        except (Contract.DoesNotExist, ValueError, ValidationError) as e:
            raise ObjectNotFoundError(detail="Contrato não encontrado.") from e

    @staticmethod
    @transaction.atomic
    def create(company: Company, payload: ContractIn) -> Contract:
        logger.info(f"Iniciando criação de Contrato para company_id={company.id}")

        data = payload.model_dump(exclude_unset=True)

        wedding_input = data.pop("wedding", None)
        supplier_input = data.pop("supplier", None)
        pdf_file_key = data.pop("pdf_file_key", None)

        # Resolução do Casamento
        if isinstance(wedding_input, Wedding):
            wedding = wedding_input
        else:
            wedding = get_object_or_404_for_tenant(
                Wedding,
                company,
                wedding_input,
                code="wedding_not_found_or_denied",
            )

        # Resolução do Fornecedor
        if isinstance(supplier_input, Supplier):
            supplier = supplier_input
        else:
            supplier = get_object_or_404_for_tenant(
                Supplier,
                company,
                supplier_input,
                code="supplier_not_found_or_denied",
            )

        parent_input = data.pop("parent", None)
        parent = None
        if parent_input:
            parent = get_object_or_404_for_tenant(
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
        contract_data: ContractIn,
        items_data: _ItemInList | None = None,
        expense_data: ExpenseIn | None = None,
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

        contract = ContractService.create(company=company, payload=contract_data)

        if pdf_file_key:
            contract.pdf_file = pdf_file_key
            contract.save(update_fields=["pdf_file"])

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
            ExpenseService.create(
                company=company,
                payload=expense_data.model_copy(update={"contract": contract.uuid}),
            )

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
            parent = get_object_or_404_for_tenant(
                Contract,
                company,
                parent_input,
                detail="Contrato pai inválido ou acesso negado.",
                code="parent_contract_not_found_or_denied",
            )

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
    def update(
        company: Company, instance: Contract, payload: ContractPatchIn
    ) -> Contract:
        validate_tenant_ownership(
            company,
            instance,
            detail="Contrato não encontrado ou acesso negado.",
            code="contract_not_found_or_denied",
        )
        logger.info(
            f"Atualizando Contrato uuid={instance.uuid} por company_id={company.id}"
        )

        data = payload.model_dump(exclude_unset=True)
        pdf_file_key = data.pop("pdf_file_key", None)
        if pdf_file_key is not None:
            instance.pdf_file = pdf_file_key

        supplier_input = data.pop("supplier", None)
        if supplier_input:
            if isinstance(supplier_input, Supplier):
                instance.supplier = supplier_input
            else:
                instance.supplier = get_object_or_404_for_tenant(
                    Supplier,
                    company,
                    supplier_input,
                    detail="Fornecedor inválido ou acesso negado.",
                    code="supplier_not_found_or_denied",
                )

        parent_input = data.pop("parent", None)
        if parent_input is not None:
            ContractService._resolve_parent(company, instance, parent_input)

        status_input = data.pop("status", None)
        if status_input is not None and status_input != instance.status:
            instance.status = status_input

        ContractService._apply_fields(instance, data)

        try:
            instance.save()
        except ValidationError as e:
            raise BusinessRuleViolation(
                detail="; ".join(e.messages),
                code="contract_update_validation_error",
            ) from e

        logger.info(f"Contrato uuid={instance.uuid} atualizado com sucesso.")
        return instance

    @staticmethod
    def _apply_fields(instance: Contract, data: dict[str, Any]) -> None:
        for field, value in data.items():
            if field == "pdf_file" and value is None:
                continue
            setattr(instance, field, value)

    @staticmethod
    @transaction.atomic
    def delete(company: Company, instance: Contract) -> None:
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

        instance.status = new_status
        try:
            instance.save()
        except ValidationError as e:
            raise BusinessRuleViolation(
                detail="; ".join(e.messages),
                code="contract_invalid_status_transition",
            ) from e

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
    @transaction.atomic
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
