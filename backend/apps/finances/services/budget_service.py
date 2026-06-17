import logging
from typing import Any
from uuid import UUID

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError, QuerySet

from apps.core.exceptions import DomainIntegrityError, ObjectNotFoundError
from apps.core.tenant import validate_tenant_ownership
from apps.finances.models import Budget
from apps.tenants.models import Company
from apps.weddings.models import Wedding


logger = logging.getLogger(__name__)


class BudgetService:
    """
    Camada de serviço para gestão do orçamento mestre.
    Garante que cada casamento tenha exatamente UM teto financeiro (OneToOne).
    """

    @staticmethod
    def list(company: Company) -> QuerySet[Budget]:
        return Budget.objects.for_tenant(company).select_related("wedding")

    @staticmethod
    def get(company: Company, uuid: UUID | str) -> Budget:
        try:
            return (
                Budget.objects.for_tenant(company)
                .select_related("wedding")
                .get(uuid=uuid)
            )
        except Budget.DoesNotExist as e:
            raise ObjectNotFoundError(detail="Orçamento não encontrado.") from e

    @staticmethod
    @transaction.atomic
    def create(company: Company, data: dict[str, Any]) -> Budget:
        logger.info(
            f"Iniciando criação de Orçamento Mestre para company_id={company.id}"
        )

        # 1. Resolução Segura do Casamento (Suporta Instância ou UUID)
        wedding_input = data.pop("wedding", None)

        if isinstance(wedding_input, Wedding):
            wedding = wedding_input
        else:
            try:
                wedding = Wedding.objects.for_tenant(company).get(uuid=wedding_input)
            except Wedding.DoesNotExist as e:
                logger.warning(
                    f"Tentativa de criar orçamento para casamento "
                    f"inválido/negado: {wedding_input}"
                )
                raise ObjectNotFoundError(
                    detail="Casamento não encontrado ou acesso negado.",
                    code="wedding_not_found_or_denied",
                ) from e

        # 2. Instanciação em Memória
        budget = Budget(company=company, wedding=wedding, **data)

        # 3. Validação e Persistência
        try:
            budget.save()
        except (IntegrityError, ValidationError) as e:
            if isinstance(e, ValidationError):
                message_dict = getattr(e, "message_dict", {})
                other_fields = [k for k in message_dict if k != "wedding"]
                if other_fields:
                    raise e

            logger.exception(
                f"Conflito de integridade: Casamento uuid={wedding.uuid} já possui "
                f"orçamento."
            )
            raise DomainIntegrityError(
                detail="Este casamento já possui um orçamento definido. Atualize o "
                "existente em vez de criar outro.",
                code="budget_already_exists",
            ) from e

        logger.info(f"Orçamento criado com sucesso: uuid={budget.uuid}")
        return budget

    @staticmethod
    @transaction.atomic
    def update(company: Company, instance: Budget, data: dict[str, Any]) -> Budget:
        validate_tenant_ownership(
            company,
            instance,
            detail="Orçamento não encontrado ou acesso negado.",
            code="budget_not_found_or_denied",
        )
        logger.info(
            f"Atualizando Orçamento uuid={instance.uuid} por company_id={company.id}"
        )

        data.pop("wedding", None)
        data.pop("company", None)

        for field, value in data.items():
            setattr(instance, field, value)

        # O full_clean() garante a validação de regras como MinValueValidator
        instance.save()

        logger.info(f"Orçamento uuid={instance.uuid} atualizado com sucesso.")
        return instance

    @staticmethod
    @transaction.atomic
    def delete(company: Company, instance: Budget) -> None:
        validate_tenant_ownership(
            company,
            instance,
            detail="Orçamento não encontrado ou acesso negado.",
            code="budget_not_found_or_denied",
        )
        logger.info(
            f"Tentativa de deleção do Orçamento uuid={instance.uuid} por "
            f"company_id={company.id}"
        )

        try:
            instance.delete()
            logger.warning(
                f"Orçamento uuid={instance.uuid} DESTRUÍDO por company_id={company.id}"
            )

        except ProtectedError as e:
            logger.exception(
                f"Falha de integridade ao deletar Orçamento uuid={instance.uuid}: "
                "Protegido por relações filhas."
            )
            raise DomainIntegrityError(
                detail="Não é possível apagar este orçamento principal pois existem "
                "categorias e despesas vinculadas a ele.",
                code="budget_protected_error",
            ) from e

    @staticmethod
    @transaction.atomic
    def get_or_create_for_wedding(company: Company, wedding_uuid: UUID | str) -> Budget:
        """
        Retorna o Budget existente ou cria um novo para o Wedding especificado.
        """
        from apps.weddings.models import Wedding

        try:
            wedding = Wedding.objects.for_tenant(company).get(uuid=wedding_uuid)
        except Wedding.DoesNotExist as e:
            logger.warning(
                f"Tentativa de criar orçamento para casamento inválido/negado: "
                f"{wedding_uuid} por company_id={company.id}"
            )
            raise ObjectNotFoundError(
                detail="Casamento não encontrado ou acesso negado.",
                code="wedding_not_found_or_denied",
            ) from e

        budget, created = Budget.objects.get_or_create(
            company=company,
            wedding=wedding,
            defaults={"total_estimated": 0},
        )

        if created:
            # TRAVA DE SEGURANÇA (TOCTOU): serializa criação de categorias padrão
            budget = (
                Budget.objects.for_tenant(company).select_for_update().get(pk=budget.pk)
            )

            from apps.finances.services.budget_category_service import (
                BudgetCategoryService,
            )

            logger.info(
                f"Budget criado sob demanda para wedding={wedding.uuid}. "
                f"Criando categorias padrão."
            )
            BudgetCategoryService.setup_defaults(
                company=company,
                wedding=wedding,
                budget=budget,
            )
            logger.info(
                f"Budget uuid={budget.uuid} + categorias criados para "
                f"wedding={wedding.uuid}"
            )
        else:
            logger.debug(f"Budget existente retornado: uuid={budget.uuid}")

        return budget
