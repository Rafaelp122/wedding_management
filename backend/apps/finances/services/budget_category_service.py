import logging
from decimal import Decimal

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction

from apps.core.exceptions import (
    BusinessRuleViolation,
    DomainIntegrityError,
)
from apps.core.shortcuts import resolve_tenant_resource
from apps.core.tenant import validate_tenant_ownership
from apps.finances.models import Budget, BudgetCategory
from apps.finances.schemas import BudgetCategoryIn, BudgetCategoryPatchIn
from apps.tenants.models import Company
from apps.weddings.models import Wedding


logger = logging.getLogger(__name__)


class BudgetCategoryService:
    """Camada de serviço para gestão de categorias orçamentárias (BudgetCategory).

    Responsável por orquestrar a criação, atualização e exclusão de categorias,
    garantindo o isolamento multi-tenant e a conservação do teto financeiro
    (BR-F04) sob lock concorrente (select_for_update).

    Regra de Negócio:
        BR-F04 (docs/architecture/business-rules/finances/budget-category-distribution.md)
    """

    @staticmethod
    @transaction.atomic
    def create(
        company: Company,
        payload: BudgetCategoryIn,
    ) -> BudgetCategory:
        """Cria uma nova categoria orçamentária vinculada a um orçamento mestre.

        Regra de Negócio:
            BR-F04 (docs/architecture/business-rules/finances/budget-category-distribution.md)

        Efeitos Colaterais:
            - Persiste atomicamente a nova categoria orçamentária sob lock pessimista no orçamento mestre.

        Raises:
            ObjectNotFoundError: Se o orçamento mestre não for encontrado ou não pertencer ao tenant.
            BusinessRuleViolation: Se a soma das categorias exceder o teto do orçamento mestre (BR-F04).
        """
        logger.info(
            f"Iniciando criação de Categoria de Orçamento para company_id={company.id}"
        )

        data = payload.model_dump(exclude_unset=True)

        budget_input = data.pop("budget", None)

        budget = resolve_tenant_resource(
            Budget,
            company,
            budget_input,
            detail="Orçamento mestre não encontrado ou acesso negado.",
            code="budget_not_found_or_denied",
        )

        # TRAVA DE SEGURANÇA (TOCTOU): lock no budget antes de persistir
        budget = (
            Budget.objects.for_tenant(company).select_for_update().get(pk=budget.pk)
        )

        category = BudgetCategory(
            company=company, wedding=budget.wedding, budget=budget, **data
        )

        try:
            category.save()
        except DjangoValidationError as e:
            detail = "; ".join(e.messages) if hasattr(e, "messages") else str(e)
            raise BusinessRuleViolation(
                detail=detail, code="budget_cap_exceeded"
            ) from e

        logger.info(f"Categoria de Orçamento criada com sucesso: uuid={category.uuid}")
        return category

    @staticmethod
    @transaction.atomic
    def update(
        company: Company,
        instance: BudgetCategory,
        payload: BudgetCategoryPatchIn,
    ) -> BudgetCategory:
        """Atualiza uma categoria de orçamento existente.

        Regra de Negócio:
            BR-F04 (docs/architecture/business-rules/finances/budget-category-distribution.md)

        Efeitos Colaterais:
            - Atualiza e persiste os dados da categoria sob lock pessimista no orçamento mestre.

        Raises:
            BusinessRuleViolation: Se a nova alocação exceder o teto do orçamento mestre (BR-F04).
        """
        validate_tenant_ownership(
            company,
            instance,
            detail="Categoria de orçamento não encontrada ou acesso negado.",
            code="budget_category_not_found_or_denied",
        )
        logger.info(
            f"Atualizando Categoria uuid={instance.uuid} por company_id={company.id}"
        )

        updated_fields: set[str] = set()
        data = payload.model_dump(exclude_unset=True)

        for field, value in data.items():
            setattr(instance, field, value)
            updated_fields.add(field)

        # TRAVA DE SEGURANÇA (TOCTOU): lock no budget antes de re-validar teto
        Budget.objects.for_tenant(company).select_for_update().get(
            pk=instance.budget.pk
        )

        if updated_fields:
            updated_fields.add("updated_at")
            try:
                instance.save(update_fields=list(updated_fields))
            except DjangoValidationError as e:
                detail = "; ".join(e.messages) if hasattr(e, "messages") else str(e)
                raise BusinessRuleViolation(
                    detail=detail, code="budget_cap_exceeded"
                ) from e

        logger.info(f"Categoria uuid={instance.uuid} atualizada com sucesso.")
        return instance

    @staticmethod
    @transaction.atomic
    def delete(company: Company, instance: BudgetCategory) -> None:
        """Exclui uma categoria de orçamento existente.

        Regra de Negócio:
            BR-F04 (docs/architecture/business-rules/finances/budget-category-distribution.md)

        Efeitos Colaterais:
            - Remove fisicamente a categoria de orçamento do banco de dados.

        Raises:
            DomainIntegrityError: Se a categoria possuir despesas vinculadas (BR-F04-D).
        """
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

        expense_count = instance.expenses.count()
        if expense_count > 0:
            logger.warning(
                f"Falha de integridade ao deletar Categoria uuid={instance.uuid}: "
                f"Possui {expense_count} despesas ativas."
            )
            raise DomainIntegrityError(
                detail=(
                    f"Não é possível apagar a categoria '{instance.name}' pois já existem "
                    f"{expense_count} despesas vinculadas a ela. Remova as despesas primeiro."
                ),
                code="category_protected_error",
            )

        instance.delete()
        logger.warning(
            f"Categoria uuid={instance.uuid} DESTRUÍDA por company_id={company.id}"
        )

    @staticmethod
    @transaction.atomic
    def setup_defaults(company: Company, wedding: Wedding, budget: Budget) -> None:
        """Cria as categorias iniciais canônicas para um novo casamento.

        Regra de Negócio:
            BR-F04 (docs/architecture/business-rules/finances/budget-category-distribution.md)

        Efeitos Colaterais:
            - Persiste em lote (bulk_create) as categorias padrão que ainda não existirem para o orçamento.
        """
        logger.info(f"Gerando categorias padrão para o casamento {wedding.uuid}")

        existing_names = set(
            BudgetCategory.objects.for_tenant(company)
            .filter(budget=budget)
            .values_list("name", flat=True)
        )

        new_names = [n for n in BudgetCategory.DEFAULT_NAMES if n not in existing_names]
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
