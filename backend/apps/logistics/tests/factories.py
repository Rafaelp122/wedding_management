"""
Fábricas de Logística (Logistics Factories).

Este ficheiro define os blueprints para Fornecedores, Contratos e Itens.
É essencial para testar a gestão de fornecedores e a entrega de serviços.

Destaques Técnicos:
- Integridade de Posse: O Supplier pertence a um User (Planner) via UserOwnedModel.
- Integridade de Tenant: Garante que o Contrato, o Fornecedor e o Casamento
  estejam vinculados ao mesmo Planner.
- Dados Reais: Usa Faker pt_BR para CNPJ, moradas e telefones brasileiros.
"""

from decimal import Decimal

import factory

from apps.finances.tests.factories import ExpenseFactory
from apps.users.tests.factories import UserFactory
from apps.weddings.tests.factories import WeddingFactory

from ..models import Contract, Item, Supplier


class SupplierFactory(factory.django.DjangoModelFactory):
    """Fábrica para Fornecedores (conforme modelo Supplier)."""

    class Meta:
        model = Supplier

    # Supplier herda de UserOwnedModel, portanto pertence a um User (Planner)
    user = factory.SubFactory(UserFactory)

    name = factory.Faker("company")
    cnpj = factory.LazyAttribute(
        lambda _: "00.000.000/0001-00"
    )  # Exemplo estático ou via Faker se disponível

    # Contacto
    phone = factory.Faker("phone_number")
    email = factory.Faker("company_email")
    website = factory.Faker("url")

    # Endereço
    address = factory.Faker("street_address")
    city = factory.Faker("city")
    state = factory.Faker("state_abbr")  # Garante apenas 2 caracteres

    notes = factory.Faker("sentence")
    is_active = True


class ContractFactory(factory.django.DjangoModelFactory):
    """
    Fábrica para Contratos de Serviço.
    Garante que o fornecedor e o casamento pertençam ao mesmo Planner.
    """

    class Meta:
        model = Contract

    wedding = factory.SubFactory(WeddingFactory)

    # O Supplier deve pertencer ao Planner do Wedding para manter a consistência
    supplier = factory.SubFactory(
        SupplierFactory, user=factory.SelfAttribute("..wedding.planner")
    )

    # Opcional: vincula a uma despesa do mesmo casamento
    expense = factory.SubFactory(
        ExpenseFactory, wedding=factory.SelfAttribute("..wedding")
    )

    contract_number = factory.Sequence(lambda n: f"CT-{2026}-{n:04d}")
    service_description = factory.Faker("paragraph")
    total_amount = Decimal("5000.00")
    status = Contract.StatusChoices.SIGNED


class ItemFactory(factory.django.DjangoModelFactory):
    """Fábrica para Itens de um contrato."""

    class Meta:
        model = Item

    wedding = factory.SubFactory(WeddingFactory)
    contract = factory.SubFactory(
        ContractFactory, wedding=factory.SelfAttribute("..wedding")
    )

    name = factory.Faker("word")
    quantity = factory.Iterator([10, 50, 100])
    description = factory.Faker("sentence")
