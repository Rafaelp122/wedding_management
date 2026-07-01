import logging
from decimal import Decimal
from uuid import UUID

from django.db import transaction
from django.db.models import ProtectedError, QuerySet, Sum

from apps.core.exceptions import (
    BusinessRuleViolation,
    DomainIntegrityError,
)
from apps.core.shortcuts import get_object_or_404_for_tenant
from apps.core.tenant import validate_tenant_ownership
from apps.finances.models import Budget, BudgetCategory
from apps.finances.schemas import BudgetCategoryIn, BudgetCategoryPatchIn
from apps.tenants.models import Company
from apps.weddings.models import Wedding


logger = logging.getLogger(__name__)


def _validate_budget_cap(
    company: Company, category: BudgetCategory, budget: Budget
) -> None:
    """
    Valida que a soma do allocated_budget de todas as categorias não excede
    o teto do orçamento mestre.
    Executada DENTRO de um ``select_for_update()`` para evitar TOCTOU.
    """
    siblings_agg = (
        BudgetCategory.objects.for_tenant(company)
        .filter(budget=budget)
        .exclude(pk=category.pk)
        .aggregate(total=Sum("allocated_budget"))
    )
    allocated_siblings = siblings_agg["total"] or Decimal("0.00")
    if allocated_siblings + category.allocated_budget > budget.total_estimated:
        raise BusinessRuleViolation(
            detail=(
                f"A soma das categorias alocadas "
                f"({allocated_siblings + category.allocated_budget}) "
                f"excede o teto do orçamento ({budget.total_estimated})."
            ),
            code="budget_cap_exceeded",
        )


class BudgetCategoryService:
    """
    Camada de serviço para gestão de categorias de orçamento.
    Validação de teto financeiro (_validate_budget_cap) executada com
    select_for_update() para evitar TOCTOU.
    """

    @staticmethod
    def list(
        company: Company, wedding_id: UUID | None = None
    ) -> QuerySet[BudgetCategory]:
        """
        Lista categorias de orçamento de uma empresa.
        """
        qs = (
            BudgetCategory.objects.for_tenant(company)
            .with_total_spent()
            .select_related("budget", "wedding")
        )
        if wedding_id:
            qs = qs.filter(wedding__uuid=wedding_id)
        return qs

    @staticmethod
    def get(company: Company, uuid: UUID | str) -> BudgetCategory:
        from django.core.exceptions import ValidationError

        from apps.core.exceptions import ObjectNotFoundError

        try:
            return (
                BudgetCategory.objects.for_tenant(company)
                .with_total_spent()
                .select_related("budget", "wedding")
                .get(uuid=uuid)
            )
        except (BudgetCategory.DoesNotExist, ValueError, ValidationError) as e:
            raise ObjectNotFoundError(
                detail="Categoria de orçamento não encontrada."
            ) from e

    @staticmethod
    @transaction.atomic
    def create(company: Company, payload: BudgetCategoryIn) -> BudgetCategory:
        logger.info(
            f"Iniciando criação de Categoria de Orçamento para company_id={company.id}"
        )

        data = payload.model_dump(exclude_unset=True)

        budget_input = data.pop("budget", None)

        if isinstance(budget_input, Budget):
            budget = budget_input
        else:
            budget = get_object_or_404_for_tenant(
                Budget,
                company,
                budget_input,
                detail="Orçamento mestre não encontrado ou acesso negado.",
                code="budget_not_found_or_denied",
            )

        # TRAVA DE SEGURANÇA (TOCTOU): lock no budget antes de ler soma das categorias
        budget = (
            Budget.objects.for_tenant(company).select_for_update().get(pk=budget.pk)
        )

        category = BudgetCategory(
            company=company, wedding=budget.wedding, budget=budget, **data
        )

        category.full_clean()
        _validate_budget_cap(company, category, budget)

        category.save(skip_clean=True)

        logger.info(f"Categoria de Orçamento criada com sucesso: uuid={category.uuid}")
        return category

    @staticmethod
    @transaction.atomic
    def update(
        company: Company,
        instance: BudgetCategory,
        payload: BudgetCategoryPatchIn,
    ) -> BudgetCategory:
        validate_tenant_ownership(
            company,
            instance,
            detail="Categoria de orçamento não encontrada ou acesso negado.",
            code="budget_category_not_found_or_denied",
        )
        logger.info(
            f"Atualizando Categoria uuid={instance.uuid} por company_id={company.id}"
        )

        data = payload.model_dump(exclude_unset=True)

        for field, value in data.items():
            setattr(instance, field, value)

        # TRAVA DE SEGURANÇA (TOCTOU): lock no budget antes de re-validar teto
        budget = (
            Budget.objects.for_tenant(company)
            .select_for_update()
            .get(pk=instance.budget.pk)
        )

        instance.full_clean()
        _validate_budget_cap(company, instance, budget)

        instance.save(skip_clean=True)

        logger.info(f"Categoria uuid={instance.uuid} atualizada com sucesso.")
        return instance

    @staticmethod
    @transaction.atomic
    def delete(company: Company, instance: BudgetCategory) -> None:
        validate_tenant_ownership(
            company,
            instance,
            detail="Categoria de orçamento não encontrada ou acesso negado.",
            code="budget_category_not_found_or_denied",
        )
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
            logger.exception(
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
    @transaction.atomic
    def setup_defaults(company: Company, wedding: Wedding, budget: Budget) -> None:
        """
        Cria as categorias iniciais obrigatórias para um novo casamento.
        É idempotente: se as categorias já existirem, não duplica.

        Nota de segurança (TOCTOU): espera-se que o budget esteja protegido
        por ``select_for_update()`` no chamador (ex: get_or_create_for_wedding).
        O ``ignore_conflicts=True`` no bulk_create protege contra o cenário
        residual de chamada direta sem lock.
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

        existing_names = set(
            BudgetCategory.objects.for_tenant(company)
            .filter(budget=budget)
            .values_list("name", flat=True)
        )

        new_names = [n for n in DEFAULT_CATEGORIES if n not in existing_names]
        if not new_names:
            logger.info(f"Categorias padrão já existem para budget={budget.uuid}")
            return

        categories = [
            BudgetCategory(
                company=company,
                wedding=wedding,
                budget=budget,
                name=name,
                allocated_budget=Decimal("0.00"),
            )
            for name in new_names
        ]

        for cat in categories:
            cat.full_clean()

        BudgetCategory.objects.bulk_create(categories, ignore_conflicts=True)
