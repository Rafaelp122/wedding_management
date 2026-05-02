import logging
from typing import Any
from uuid import UUID

from django.db import transaction
from django.db.models import ProtectedError, QuerySet

from apps.core.exceptions import (
    DomainIntegrityError,
    ObjectNotFoundError,
)
from apps.finances.models import BudgetCategory
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
        company: Company, wedding_id: UUID | str | None = None
    ) -> QuerySet[Contract]:
        qs = Contract.objects.for_tenant(company).select_related(
            "supplier", "wedding", "budget_category"
        )
        if wedding_id:
            qs = qs.filter(wedding__uuid=wedding_id)
        return qs

    @staticmethod
    def get(company: Company, uuid: UUID | str) -> Contract:
        try:
            return (
                Contract.objects.for_tenant(company)
                .select_related("supplier", "wedding", "budget_category")
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

        # Resolução da Categoria de Orçamento
        budget_cat_input = data.pop("budget_category", None)
        budget_category = None
        if budget_cat_input:
            if isinstance(budget_cat_input, BudgetCategory):
                budget_category = budget_cat_input
            else:
                try:
                    budget_category = BudgetCategory.objects.for_tenant(company).get(
                        uuid=budget_cat_input
                    )
                except BudgetCategory.DoesNotExist as e:
                    raise ObjectNotFoundError(
                        detail="Categoria de orçamento não encontrada.",
                        code="budget_category_not_found_or_denied",
                    ) from e

        # 2. Instanciação em Memória
        contract = Contract(
            company=company,
            wedding=wedding,
            supplier=supplier,
            budget_category=budget_category,
            **data,
        )

        # 3. Validação Estrita (O Model aplica as suas regras, incluindo checagem de
        # datas)
        contract.save()

        logger.info(f"Contrato criado com sucesso: uuid={contract.uuid}")
        return contract

    @staticmethod
    @transaction.atomic
    def update(company: Company, instance: Contract, data: dict[str, Any]) -> Contract:
        logger.info(
            f"Atualizando Contrato uuid={instance.uuid} por company_id={company.id}"
        )

        # Proteção contra sequestro de propriedade
        data.pop("wedding", None)
        data.pop("company", None)

        # Troca de Fornecedor (com validação multitenant)
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

        # Troca de Categoria de Orçamento (com validação multitenant)
        budget_cat_input = data.pop("budget_category", None)
        if budget_cat_input is not None:
            if isinstance(budget_cat_input, BudgetCategory):
                instance.budget_category = budget_cat_input
            elif budget_cat_input == "":
                instance.budget_category = None
            else:
                try:
                    instance.budget_category = BudgetCategory.objects.for_tenant(
                        company
                    ).get(uuid=budget_cat_input)
                except BudgetCategory.DoesNotExist as e:
                    raise ObjectNotFoundError(
                        detail="Categoria de orçamento inválida ou acesso negado.",
                        code="budget_category_not_found_or_denied",
                    ) from e

        # Atualização dinâmica de campos
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
            logger.error(
                f"Falha de integridade ao deletar contrato uuid={instance.uuid}"
            )
            raise DomainIntegrityError(
                detail="Não é possível apagar este contrato pois existem registros "
                "financeiros (parcelas) vinculados a ele. Apague as parcelas primeiro.",
                code="contract_protected_error",
            ) from e
