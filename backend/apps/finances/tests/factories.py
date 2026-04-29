"""
Fábricas de Finanças (Finances Factories).
"""

from decimal import Decimal

import factory

from apps.events.tests.factories import EventFactory
from apps.finances.models import Budget, BudgetCategory, Expense, Installment


class BudgetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Budget

    event = factory.SubFactory(EventFactory)
    total_estimated = Decimal("50000.00")


class BudgetCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BudgetCategory

    # Precisamos do event aqui para que o SelfAttribute funcione
    event = factory.SubFactory(EventFactory)

    budget = factory.SubFactory(BudgetFactory, event=factory.SelfAttribute("..event"))
    name = factory.Iterator(
        ["Buffet", "Decoração", "Fotografia", "Música", "Espaço", "Convites"]
    )
    allocated_budget = Decimal("5000.00")


class ExpenseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Expense

    event = factory.SubFactory(EventFactory)

    category = factory.SubFactory(
        BudgetCategoryFactory,
        event=factory.SelfAttribute("..event"),
    )

    contract = factory.SubFactory(
        "apps.logistics.tests.factories.ContractFactory",
        event=factory.SelfAttribute("..event"),
    )

    actual_amount = Decimal("0.00")
    description = factory.Faker("sentence")
    estimated_amount = factory.Faker(
        "pydecimal", left_digits=5, right_digits=2, positive=True
    )


class InstallmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Installment

    # O event vem da despesa
    event = factory.SelfAttribute("expense.event")
    expense = factory.SubFactory(ExpenseFactory)
    installment_number = factory.Sequence(lambda n: n + 1)
    amount = Decimal("500.00")
    due_date = factory.Faker("future_date")
    status = Installment.StatusChoices.PENDING
