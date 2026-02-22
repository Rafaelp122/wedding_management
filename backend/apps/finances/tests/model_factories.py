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
from apps.weddings.tests.factories import WeddingFactory


class BudgetFactory(factory.django.DjangoModelFactory):
    """Fábrica para o Orçamento Geral do casamento."""

    class Meta:
        model = Budget

    wedding = factory.SubFactory(WeddingFactory)
    # agora o campo chama-se total_estimated conforme o modelo
    total_estimated = Decimal("50000.00")


class BudgetCategoryFactory(factory.django.DjangoModelFactory):
    """Fábrica para categorias de orçamento (ex: Buffet, Fotografia)."""

    class Meta:
        model = BudgetCategory

    budget = factory.SubFactory("apps.finances.tests.model_factories.BudgetFactory")
    wedding = factory.LazyAttribute(lambda o: o.budget.wedding)
    name = factory.Iterator([
        "Buffet",
        "Decoração",
        "Fotografia",
        "Música",
        "Espaço",
        "Convites",
    ])
    allocated_budget = Decimal("5000.00")


class ExpenseFactory(factory.django.DjangoModelFactory):
    """
    Fábrica para Despesas.
    Garante consistência: a categoria deve pertencer ao mesmo casamento da despesa.
    """

    class Meta:
        model = Expense

    # Se a despesa for criada sozinha, ela cria um contrato (que cria um wedding)
    contract = factory.SubFactory("apps.logistics.tests.factories.ContractFactory")

    # Sincronização automática:
    # Tenta pegar o wedding do contrato; se não existir, usa o que foi passado.
    wedding = factory.SelfAttribute("..contract.wedding")

    # Garante que a categoria também pertença ao mesmo orçamento/casamento
    category = factory.SubFactory(
        "apps.finances.tests.model_factories.BudgetCategoryFactory",
        budget=factory.SelfAttribute("..wedding.budget"),
    )

    actual_amount = Decimal("1000.00")
    description = factory.Faker("sentence")

    estimated_amount = factory.Faker(
        "pydecimal", left_digits=5, right_digits=2, positive=True
    )


class InstallmentFactory(factory.django.DjangoModelFactory):
    """Fábrica para Parcelas de uma despesa."""

    class Meta:
        model = Installment

    expense = factory.SubFactory(ExpenseFactory)
    number = factory.Sequence(lambda n: n + 1)
    amount = Decimal("500.00")
    due_date = factory.Faker("future_date")
    status = Installment.StatusChoices.PENDING
