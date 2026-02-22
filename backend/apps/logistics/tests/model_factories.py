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
from django.utils import timezone

from apps.logistics.models import Contract, Item, Supplier
from apps.users.tests.factories import UserFactory
from apps.weddings.tests.factories import WeddingFactory


class SupplierFactory(factory.django.DjangoModelFactory):
    """Fábrica para Fornecedores (conforme modelo Supplier)."""

    class Meta:
        model = Supplier

    # Supplier herda de PlannerOwnedMixin, portanto pertence a um User (Planner)
    planner = factory.SubFactory(UserFactory)

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
    class Meta:
        model = Contract

    wedding = factory.SubFactory("apps.weddings.tests.factories.WeddingFactory")

    # Sincroniza o planner do fornecedor com o do casamento
    supplier = factory.SubFactory(
        "apps.logistics.tests.model_factories.SupplierFactory",
        planner=factory.SelfAttribute("..wedding.planner"),
    )

    # Corrigido: Nome do campo no model é 'description'
    description = factory.Faker("paragraph")
    total_amount = Decimal("5000.00")

    # Se usar SIGNED, precisamos satisfazer o clean() do Model
    status = Contract.StatusChoices.SIGNED
    signed_date = factory.LazyFunction(timezone.now)

    # Gera um arquivo PDF fake para passar na validação do clean()
    pdf_file = factory.django.FileField(
        filename="contrato_fake.pdf", content=b"fake content"
    )

    # Mantemos o RelatedFactory para a Expense (Despesa)
    # factory_related_name="contract" vincula a Expense ao Contract criado aqui
    expense_rel = factory.RelatedFactory(
        "apps.finances.tests.model_factories.ExpenseFactory",
        factory_related_name="contract",
        # Forçamos a despesa a usar o MESMO wedding do contrato
        wedding=factory.SelfAttribute("..wedding"),
        estimated_amount=factory.SelfAttribute("..total_amount"),
        actual_amount=factory.SelfAttribute("..total_amount"),
    )

    # Campos adicionais do modelo
    expiration_date = factory.Faker("future_date")
    alert_days_before = 30


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
