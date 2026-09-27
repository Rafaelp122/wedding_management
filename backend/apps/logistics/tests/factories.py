"""
Fábricas de Logística (Logistics Factories).

Este ficheiro define os blueprints para Fornecedores, Contratos e Itens.
É essencial para testar a gestão de fornecedores e a entrega de serviços.

Destaques Técnicos:
- Integridade de Posse: O Supplier pertence a um User (Planner) via PlannerOwnedMixin.
- Integridade de Tenant: Garante que o Contrato, o Fornecedor e o Casamento
  estejam vinculados ao mesmo Planner.
- Dados Reais: Usa Faker pt_BR para CNPJ, moradas e telefones brasileiros.
"""

from decimal import Decimal

import factory

from apps.contracts.models import Contract
from apps.logistics.models import Item
from apps.weddings.tests.factories import WeddingFactory


class ContractFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Contract

    wedding = factory.SubFactory("apps.weddings.tests.factories.WeddingFactory")

    # Sincroniza a empresa entre contrato, casamento e fornecedor
    company = factory.SelfAttribute("wedding.company")
    supplier = factory.SubFactory(
        "apps.contracts.tests.factories.SupplierFactory",
        company=factory.SelfAttribute("..company"),
    )

    name = factory.Faker("sentence", nb_words=3)
    description = factory.Faker("paragraph")
    total_amount = Decimal("5000.00")

    # DRAFT por default (evita side effects de Expense via RelatedFactory)
    status = Contract.StatusChoices.DRAFT

    expiration_date = factory.Faker("future_date")
    alert_days_before = 30


class ItemFactory(factory.django.DjangoModelFactory):
    """Fábrica para Itens de um contrato."""

    class Meta:
        model = Item

    wedding = factory.SubFactory(WeddingFactory)
    company = factory.SelfAttribute("wedding.company")
    contract = factory.SubFactory(
        ContractFactory, wedding=factory.SelfAttribute("..wedding")
    )

    name = factory.Faker("word")
    quantity = factory.Iterator([10, 50, 100])
    description = factory.Faker("sentence")
