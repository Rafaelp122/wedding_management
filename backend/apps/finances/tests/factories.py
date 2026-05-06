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
    company = factory.SelfAttribute("wedding.company")
    total_estimated = Decimal("50000.00")


class BudgetCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BudgetCategory

    wedding = factory.SelfAttribute("budget.wedding")
    company = factory.SelfAttribute("wedding.company")
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
    company = factory.SelfAttribute("wedding.company")

    category = factory.SubFactory(
        BudgetCategoryFactory,
        budget=factory.SubFactory(
            BudgetFactory,
            wedding=factory.SelfAttribute("..wedding"),
        ),
    )

    contract = factory.SubFactory(
        "apps.logistics.tests.factories.ContractFactory",
        wedding=factory.SelfAttribute("..wedding"),
    )

    name = factory.Faker("sentence", nb_words=3)
    actual_amount = Decimal("1000.00")
    description = factory.Faker("sentence")
    estimated_amount = factory.Faker(
        "pydecimal", left_digits=5, right_digits=2, positive=True
    )


class InstallmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Installment

    wedding = factory.SelfAttribute("expense.wedding")
    company = factory.SelfAttribute("wedding.company")
    expense = factory.SubFactory(ExpenseFactory)
    installment_number = factory.Sequence(lambda n: n + 1)
    amount = Decimal("500.00")
    due_date = factory.Faker("future_date")
    status = Installment.StatusChoices.PENDING
