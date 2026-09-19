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
    """

    @staticmethod
    @transaction.atomic
    def create(
        company: Company,
        payload: BudgetCategoryIn,
    ) -> BudgetCategory:
        """Cria uma nova categoria orçamentária vinculada a um orçamento mestre.

        Obtém lock pessimista no orçamento mestre para evitar condição de corrida
        (TOCTOU) e delega a validação de conservação do teto ao BudgetCategory.clean()
        via BaseModel.save().

        Args:
            company: O tenant atual para isolamento de dados.
            payload: Dados de entrada validados para a categoria.

        Returns:
            BudgetCategory: A instância persistida da categoria criada.

        Raises:
            ObjectNotFoundError: Se o orçamento mestre não for encontrado.
            BusinessRuleViolation: Se a soma das categorias exceder o orçamento.
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

        Garante o isolamento do tenant e re-valida o teto do orçamento mestre
        sob lock (select_for_update) através do BaseModel.save().

        Args:
            company: O tenant atual para isolamento de dados.
            instance: A instância da categoria de orçamento a ser atualizada.
            payload: Dados parciais para atualização da categoria.

        Returns:
            BudgetCategory: A instância da categoria atualizada.

        Raises:
            BusinessRuleViolation: Se exceder o teto do orçamento mestre.
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

        Verifica se a categoria pertence ao tenant e se não possui despesas
        ativas vinculadas, prevenindo quebras de integridade.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: A instância da categoria de orçamento a ser excluída.

        Raises:
            DomainIntegrityError: Se a categoria possuir despesas vinculadas.
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

        if instance.expenses.exists():
            logger.warning(
                f"Falha de integridade ao deletar Categoria uuid={instance.uuid}: "
                "Possui despesas ativas."
            )
            raise DomainIntegrityError(
                detail=(
                    "Não é possível apagar esta categoria pois já existem "
                    "despesas vinculadas a ela. Remova as despesas primeiro."
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
        """Cria as categorias iniciais obrigatórias para um novo casamento.

        Método idempotente. Espera-se que o budget esteja protegido por
        select_for_update() no chamador para evitar condições de corrida.

        Args:
            company: O tenant atual para isolamento de dados.
            wedding: A instância do casamento correspondente.
            budget: A instância do orçamento mestre associado.
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
