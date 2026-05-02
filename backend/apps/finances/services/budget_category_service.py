import logging
from typing import Any
from uuid import UUID

from django.db import transaction
from django.db.models import ProtectedError, QuerySet

from apps.core.exceptions import (
    DomainIntegrityError,
    ObjectNotFoundError,
)
from apps.finances.models import Budget, BudgetCategory
from apps.tenants.models import Company
from apps.weddings.models import Wedding


logger = logging.getLogger(__name__)


class BudgetCategoryService:
    """
    Camada de serviço para gestão de categorias de orçamento.
    Delega a validação matemática rigorosa de teto financeiro para o Model.
    """

    @staticmethod
    def list(
        company: Company, wedding_id: UUID | None = None
    ) -> QuerySet[BudgetCategory]:
        """
        Lista categorias de orçamento de uma empresa.
        """
        qs = BudgetCategory.objects.for_tenant(company).select_related(
            "budget", "wedding"
        )
        if wedding_id:
            qs = qs.filter(wedding__uuid=wedding_id)
        return qs

    @staticmethod
    def get(company: Company, uuid: UUID | str) -> BudgetCategory:
        try:
            return (
                BudgetCategory.objects.for_tenant(company)
                .select_related("budget", "wedding")
                .get(uuid=uuid)
            )
        except BudgetCategory.DoesNotExist as e:
            raise ObjectNotFoundError(
                detail="Categoria de orçamento não encontrada."
            ) from e

    @staticmethod
    @transaction.atomic
    def create(company: Company, data: dict[str, Any]) -> BudgetCategory:
        logger.info(
            f"Iniciando criação de Categoria de Orçamento para company_id={company.id}"
        )

        # 1. Resolução Segura do Orçamento Pai (Suporta Instância ou UUID)
        budget_input = data.pop("budget", None)

        if isinstance(budget_input, Budget):
            budget = budget_input
        else:
            try:
                # Segurança estrita: Garante posse da empresa sobre o orçamento
                budget = Budget.objects.for_tenant(company).get(uuid=budget_input)
            except Budget.DoesNotExist as e:
                logger.warning(
                    f"Tentativa de uso de orçamento inválido/negado: {budget_input}"
                )
                raise ObjectNotFoundError(
                    detail="Orçamento mestre não encontrado ou acesso negado.",
                    code="budget_not_found_or_denied",
                ) from e

        # 2. Injeção de Contexto e Instanciação
        category = BudgetCategory(
            company=company, wedding=budget.wedding, budget=budget, **data
        )

        # 3. Delegação de Validação ao Model
        category.save()

        logger.info(f"Categoria de Orçamento criada com sucesso: uuid={category.uuid}")
        return category

    @staticmethod
    @transaction.atomic
    def update(
        company: Company, instance: BudgetCategory, data: dict[str, Any]
    ) -> BudgetCategory:
        logger.info(
            f"Atualizando Categoria uuid={instance.uuid} por company_id={company.id}"
        )

        # Proteção contra sequestro/mudança de árvore financeira
        data.pop("budget", None)
        data.pop("wedding", None)
        data.pop("company", None)

        for field, value in data.items():
            setattr(instance, field, value)

        instance.save()

        logger.info(f"Categoria uuid={instance.uuid} atualizada com sucesso.")
        return instance

    @staticmethod
    @transaction.atomic
    def delete(company: Company, instance: BudgetCategory) -> None:
        logger.info(
            f"Tentativa de deleção da Categoria uuid={instance.uuid} "
            f"por company_id={company.id}"
        )

        try:
            instance.delete()
            logger.warning(
                f"Categoria uuid={instance.uuid} DESTRUÍDA por company_id={company.id}"
            )

        except ProtectedError as e:
            logger.error(
                f"Falha de integridade ao deletar Categoria uuid={instance.uuid}: "
                "Possui despesas ativas."
            )
            raise DomainIntegrityError(
                detail=(
                    "Não é possível apagar esta categoria pois já existem "
                    "despesas vinculadas a ela. Remova as despesas primeiro."
                ),
                code="category_protected_error",
            ) from e

    @staticmethod
    def setup_defaults(company: Company, wedding: Wedding, budget: Budget) -> None:
        """
        Cria as categorias iniciais obrigatórias para um novo casamento.
        """
        DEFAULT_CATEGORIES = [
            "Espaço e Buffet",
            "Decoração e Flores",
            "Fotografia e Vídeo",
            "Música e Iluminação",
            "Assessoria",
            "Trajes e Beleza",
        ]

        logger.info(f"Gerando categorias padrão para o casamento {wedding.uuid}")

        categories = [
            BudgetCategory(
                company=company,
                wedding=wedding,
                budget=budget,
                name=name,
                allocated_budget=0,
            )
            for name in DEFAULT_CATEGORIES
        ]

        BudgetCategory.objects.bulk_create(categories)
