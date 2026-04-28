from uuid import UUID

from django.http import HttpRequest

from apps.finances.models import Budget, BudgetCategory, Expense, Installment


def get_budget(request: HttpRequest, uuid: UUID) -> Budget:
    """Injeta a instância de Budget validada para o usuário logado."""
    return Budget.objects.resolve(request.user, uuid)


def get_budget_category(request: HttpRequest, uuid: UUID) -> BudgetCategory:
    """Injeta a instância de BudgetCategory validada para o usuário logado."""
    return BudgetCategory.objects.resolve(request.user, uuid)


def get_expense(request: HttpRequest, uuid: UUID) -> Expense:
    """Injeta a instância de Expense validada para o usuário logado."""
    return Expense.objects.resolve(request.user, uuid)


def get_installment(request: HttpRequest, uuid: UUID) -> Installment:
    """Injeta a instância de Installment validada para o usuário logado."""
    return Installment.objects.resolve(request.user, uuid)
