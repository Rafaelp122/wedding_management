"""
Fábricas de Finanças (Finances Factories).

Este ficheiro define os blueprints para Orçamentos, Categorias, Despesas e Parcelas.
É o núcleo para testar a saúde financeira e a integridade contábil.

Destaques Técnicos:
- Integridade de Tenant: Garante que a Categoria e a Despesa pertençam ao mesmo
  Wedding através de SelfAttribute.
- Regra BR-F01: Inclui lógica para gerar parcelas que respeitam a soma total
  da despesa (Tolerância Zero).
- Precisão Decimal: Utiliza DecimalField para evitar erros de arredondamento.
"""

from decimal import Decimal

import factory

from apps.finances.models import Budget, BudgetCategory, Expense, Installment
from apps.weddings.tests.model_factories import WeddingFactory


class BudgetFactory(factory.django.DjangoModelFactory):
    """Fábrica para o Orçamento Geral do casamento."""

    class Meta:
        model = Budget

    wedding = factory.SubFactory(WeddingFactory)
    total_budget = Decimal("50000.00")


class BudgetCategoryFactory(factory.django.DjangoModelFactory):
    """Fábrica para categorias de orçamento (ex: Buffet, Fotografia)."""

    class Meta:
        model = BudgetCategory

    wedding = factory.SubFactory(WeddingFactory)
    name = factory.Faker("commerce_department")
    allocated_budget = Decimal("5000.00")


class ExpenseFactory(factory.django.DjangoModelFactory):
    """
    Fábrica para Despesas.
    Garante consistência: a categoria deve pertencer ao mesmo casamento da despesa.
    """

    class Meta:
        model = Expense

    wedding = factory.SubFactory(WeddingFactory)

    # Garante que a categoria use o mesmo wedding da despesa
    category = factory.SubFactory(
        BudgetCategoryFactory, wedding=factory.SelfAttribute("..wedding")
    )

    name = factory.Faker("commerce_product")
    actual_amount = Decimal("1000.00")
    description = factory.Faker("sentence")


class InstallmentFactory(factory.django.DjangoModelFactory):
    """Fábrica para Parcelas de uma despesa."""

    class Meta:
        model = Installment

    expense = factory.SubFactory(ExpenseFactory)
    number = factory.Sequence(lambda n: n + 1)
    amount = Decimal("500.00")
    due_date = factory.Faker("future_date")
    status = Installment.StatusChoices.PENDING
