import logging
from decimal import Decimal
from typing import Any
from uuid import UUID

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
from apps.finances.models import Expense, Installment
from apps.logistics.models import Contract, Supplier
from apps.tenants.models import Company
from apps.weddings.models import Wedding


logger = logging.getLogger(__name__)


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
                .select_related("supplier", "wedding", "parent", "expense")
                .annotate(addendums_count=Count("addendums"))
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
            **data,
        )

        # 3. Validação Estrita (O Model aplica as suas regras, incluindo checagem de
        # datas)
        contract.save()

        logger.info(f"Contrato criado com sucesso: uuid={contract.uuid}")
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
        allowed_transitions: dict[str, list[str]] = {
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
    def upload_file(company: Company, uuid: UUID | str, uploaded_file: Any) -> Contract:
        """
        Faz upload de um arquivo (PDF, PNG, JPEG) para o contrato.
        Salva no storage configurado e persiste a referência no modelo.
        """
        logger.info(f"Upload de arquivo para contrato uuid={uuid}")

        # Defesa em camadas: o service valida MIME (content_type do UploadedFile)
        # como fast-fail antes de I/O; o modelo valida extensão via
        # FileExtensionValidator no clean(). MIME não é acessível no modelo,
        # extensão não é confiável isoladamente — os critérios são complementares.
        allowed_content_types = [
            "application/pdf",
            "image/png",
            "image/jpeg",
        ]
        file_content_type = getattr(uploaded_file, "content_type", None)
        if file_content_type is None:
            logger.warning(
                f"Upload sem Content-Type header para contrato uuid={uuid} — "
                f"validação de MIME bypassada, extensão será verificada no modelo."
            )
        elif file_content_type not in allowed_content_types:
            raise ValidationError(
                {"pdf_file": "Tipo de arquivo não suportado. Use PDF, PNG ou JPEG."}
            )

        # Fast-fail: validação de tamanho
        max_size = 10 * 1024 * 1024  # 10MB
        if uploaded_file.size is None:
            logger.warning(
                f"Upload sem size reportado para contrato uuid={uuid} — "
                f"validação de tamanho bypassada, será verificada no modelo."
            )
        elif uploaded_file.size > max_size:
            raise ValidationError({"pdf_file": "Arquivo excede o limite de 10MB."})

        contract = ContractService.get(company, uuid)
        contract.pdf_file.save(uploaded_file.name, uploaded_file, save=False)
        contract.save(update_fields=["pdf_file"])
        logger.info(f"Arquivo salvo no contrato uuid={uuid}")
        return contract

    @staticmethod
    def delete_file(company: Company, uuid: UUID | str) -> None:
        """
        Remove o arquivo vinculado ao contrato.
        """
        logger.info(f"Removendo arquivo do contrato uuid={uuid}")
        contract = ContractService.get(company, uuid)
        contract.pdf_file = None
        contract.save(update_fields=["pdf_file"])
        logger.info(f"Arquivo removido do contrato uuid={uuid}")
