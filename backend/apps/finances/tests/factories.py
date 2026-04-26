"""
Fábricas de Finanças (Finances Factories).
"""

from decimal import Decimal

import factory

from apps.finances.models import Budget, BudgetCategory, Expense, Installment
from apps.weddings.tests.factories import WeddingFactory


class BudgetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Budget

    wedding = factory.SubFactory(WeddingFactory)
    total_estimated = Decimal("50000.00")


class BudgetCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BudgetCategory

    # Precisamos do wedding aqui para que o SelfAttribute funcione
    wedding = factory.SubFactory(WeddingFactory)

    budget = factory.SubFactory(
        BudgetFactory, wedding=factory.SelfAttribute("..wedding")
    )
    name = factory.Iterator(
        ["Buffet", "Decoração", "Fotografia", "Música", "Espaço", "Convites"]
    )
    allocated_budget = Decimal("5000.00")


class ExpenseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Expense

    wedding = factory.SubFactory(WeddingFactory)

    category = factory.SubFactory(
        BudgetCategoryFactory,
        wedding=factory.SelfAttribute("..wedding"),
    )

    contract = factory.SubFactory(
        "apps.logistics.tests.factories.ContractFactory",
        wedding=factory.SelfAttribute("..wedding"),
    )

    actual_amount = Decimal("0.00")
    description = factory.Faker("sentence")
    estimated_amount = factory.Faker(
        "pydecimal", left_digits=5, right_digits=2, positive=True
    )


class InstallmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Installment

    # O wedding vem da despesa
    wedding = factory.SelfAttribute("expense.wedding")
    expense = factory.SubFactory(ExpenseFactory)
    installment_number = factory.Sequence(lambda n: n + 1)
    amount = Decimal("500.00")
    due_date = factory.Faker("future_date")
    status = Installment.StatusChoices.PENDING
