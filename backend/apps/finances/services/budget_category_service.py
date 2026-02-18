from decimal import Decimal

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import Sum

from apps.finances.dto import BudgetCategoryDTO
from apps.finances.models import Budget, BudgetCategory


class BudgetCategoryService:
    """
    Gerencia categorias de orçamento com validações de teto financeiro.
    """

    @staticmethod
    def validate_budget_ceiling(budget_id, new_amount, exclude_id=None):
        """
        Garante que a alocação não ultrapasse o teto do orçamento mestre.
        """
        budget = Budget.objects.get(uuid=budget_id)

        query = BudgetCategory.objects.filter(budget=budget)
        if exclude_id:
            query = query.exclude(id=exclude_id)

        current_allocated = query.aggregate(Sum("allocated_budget"))[
            "allocated_budget__sum"
        ] or Decimal("0.00")

        if (current_allocated + new_amount) > budget.total_estimated:
            raise DjangoValidationError(
                {
                    "allocated_budget": f"Estouro de teto: O total "
                    f"alocado(R$ {current_allocated + new_amount}) excede "
                    f"o orçamento mestre (R$ {budget.total_estimated})."
                }
            )

    @staticmethod
    @transaction.atomic
    def create(dto: BudgetCategoryDTO) -> BudgetCategory:
        """Cria uma categoria herdando o contexto do orçamento pai."""

        # 1. Busca o orçamento pai (Herança de Contexto)
        budget = Budget.objects.get(uuid=dto.budget_id)

        # 2. Validação de teto
        BudgetCategoryService.validate_budget_ceiling(budget.uuid, dto.allocated_budget)

        data = dto.model_dump()

        # 3. Limpeza para garantir a integridade relacional
        data.pop("budget_id")
        data.pop("wedding_id", None)
        data.pop("planner_id", None)

        return BudgetCategory.objects.create(
            planner=budget.planner,  # Herda do pai
            wedding=budget.wedding,  # Herda do pai (Garante ADR-009)
            budget=budget,
            **data,
        )

    @staticmethod
    @transaction.atomic
    def update(instance: BudgetCategory, dto: BudgetCategoryDTO) -> BudgetCategory:
        """Atualização protegendo campos de contexto."""
        BudgetCategoryService.validate_budget_ceiling(
            dto.budget_id, dto.allocated_budget, exclude_id=instance.id
        )

        # No update, impedimos a troca de orçamento ou casamento
        exclude_fields = {"planner_id", "wedding_id", "budget_id"}

        for field, value in dto.model_dump(exclude=exclude_fields).items():
            setattr(instance, field, value)

        instance.save()
        return instance

    @staticmethod
    @transaction.atomic
    def delete(instance: BudgetCategory) -> None:
        if instance.expenses.exists():
            raise DjangoValidationError(
                "Não é possível excluir uma categoria que já possui despesas"
                " vinculadas."
            )
        instance.delete()
