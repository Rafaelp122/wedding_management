from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum

from apps.finances.models import Budget, BudgetCategory


class BudgetCategoryService:
    """
    Gerencia categorias de orçamento com validações rigorosas de teto financeiro.
    Garante que o Planner não gaste o que não tem.
    """

    @staticmethod
    def _validate_budget_ceiling(budget, new_amount, exclude_instance_id=None):
        """
        Validação interna: impede que a soma das categorias ultrapasse o total do
        casamento.
        """
        query = BudgetCategory.objects.filter(budget=budget)
        if exclude_instance_id:
            query = query.exclude(id=exclude_instance_id)

        current_allocated = query.aggregate(Sum("allocated_budget"))[
            "allocated_budget__sum"
        ] or Decimal("0.00")
        total_after_update = current_allocated + Decimal(str(new_amount))

        if total_after_update > budget.total_estimated:
            raise ValidationError({
                "allocated_budget": f"Estouro de teto: O total alocado "
                f"(R$ {total_after_update}) excede o orçamento mestre "
                f"(R$ {budget.total_estimated})."
            })

    @staticmethod
    @transaction.atomic
    def create(user, data: dict) -> BudgetCategory:
        """
        Cria uma categoria validando a posse do orçamento e o teto disponível.
        """
        budget_uuid = data.pop("budget", None)

        # SEGURANÇA: Buscamos o orçamento garantindo que pertence ao Planner
        # autenticado.
        try:
            budget = Budget.objects.all().for_user(user).get(uuid=budget_uuid)
        except Budget.DoesNotExist:
            raise ValidationError({
                "budget": "Orçamento pai não encontrado ou acesso negado."
            }) from Budget.DoesNotExist

        allocated_budget = data.get("allocated_budget", 0)
        BudgetCategoryService._validate_budget_ceiling(budget, allocated_budget)

        # Injeção automática de contexto (Multitenancy ADR-009)
        data["planner"] = user
        data["wedding"] = budget.wedding
        data["budget"] = budget

        category = BudgetCategory(**data)
        category.full_clean()
        category.save()
        return category

    @staticmethod
    @transaction.atomic
    def update(instance: BudgetCategory, user, data: dict) -> BudgetCategory:
        """
        Atualiza a categoria revalidando o teto se o valor mudar.
        """
        # Protegemos campos imutáveis
        data.pop("budget", None)
        data.pop("wedding", None)
        data.pop("planner", None)

        new_amount = data.get("allocated_budget")
        if new_amount is not None:
            BudgetCategoryService._validate_budget_ceiling(
                instance.budget, new_amount, exclude_instance_id=instance.id
            )

        for field, value in data.items():
            setattr(instance, field, value)

        instance.full_clean()
        instance.save()
        return instance

    @staticmethod
    @transaction.atomic
    def delete(user, instance: BudgetCategory) -> None:
        """
        Impede a deleção de categorias que já possuem histórico financeiro.
        """
        # related_name 'expense_records' definido no Mixin/Model
        if instance.expense_records.exists():
            raise ValidationError(
                "Integridade Financeira: Não é possível excluir uma categoria "
                "que já possui despesas vinculadas. "
                "Remova as despesas primeiro."
            )
        instance.delete()
