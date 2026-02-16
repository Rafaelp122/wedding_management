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

        # Soma as categorias existentes
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
        BudgetCategoryService.validate_budget_ceiling(
            dto.budget_id, dto.allocated_budget
        )

        return BudgetCategory.objects.create(
            wedding_id=dto.wedding_id,
            budget_id=dto.budget_id,
            name=dto.name,
            description=dto.description,
            allocated_budget=dto.allocated_budget,
        )

    @staticmethod
    @transaction.atomic
    def update(instance: BudgetCategory, dto: BudgetCategoryDTO) -> BudgetCategory:
        BudgetCategoryService.validate_budget_ceiling(
            dto.budget_id, dto.allocated_budget, exclude_id=instance.id
        )

        instance.name = dto.name
        instance.description = dto.description
        instance.allocated_budget = dto.allocated_budget
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
