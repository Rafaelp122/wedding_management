"""
Fábricas do domínio de Contratos e Termos Aditivos (apps.contracts).
"""

from __future__ import annotations

import datetime as dt
from decimal import Decimal

import factory

from apps.contracts.models import Contract, ContractAddendum, Supplier


class SupplierFactory(factory.django.DjangoModelFactory):
    """Fábrica para Fornecedores (catálogo compartilhado do tenant)."""

    class Meta:
        model = Supplier

    company = factory.SubFactory("apps.tenants.tests.factories.CompanyFactory")

    name = factory.Faker("company")
    cnpj = factory.LazyAttribute(lambda _: "11.222.333/0001-81")

    phone = factory.Faker("phone_number")
    email = factory.Faker("company_email")
    website = factory.Faker("url")

    address = factory.Faker("street_address")
    city = factory.Faker("city")
    state = factory.Faker("state_abbr")

    notes = factory.Faker("sentence")
    is_active = True


class SupplierContractFactory(factory.django.DjangoModelFactory):
    """Fábrica padrão para contratos de fornecedores (SUPPLIER)."""

    class Meta:
        model = Contract

    wedding = factory.SubFactory("apps.weddings.tests.factories.WeddingFactory")
    company = factory.SelfAttribute("wedding.company")
    supplier = factory.SubFactory(
        "apps.contracts.tests.factories.SupplierFactory",
        company=factory.SelfAttribute("..company"),
    )
    client = None

    contract_type = Contract.ContractTypeChoices.SUPPLIER
    service_tier = None

    name = factory.Faker("sentence", nb_words=3)
    description = factory.Faker("paragraph")
    total_amount = Decimal("5000.00")
    installments_count = 1

    status = Contract.StatusChoices.DRAFT
    expiration_date = factory.Faker("future_date")
    alert_days_before = 30
    signed_date = None


class SignedSupplierContractFactory(SupplierContractFactory):
    """Fábrica para contratos de fornecedor assinados."""

    status = Contract.StatusChoices.SIGNED
    signed_date = factory.LazyFunction(dt.date.today)
    pdf_file = factory.django.FileField(filename="contrato_assinado.pdf")


class PlannerContractFactory(factory.django.DjangoModelFactory):
    """Fábrica para contratos de honorários de assessoria (PLANNER)."""

    class Meta:
        model = Contract

    wedding = factory.SubFactory("apps.weddings.tests.factories.WeddingFactory")
    company = factory.SelfAttribute("wedding.company")
    supplier = None
    client = None

    contract_type = Contract.ContractTypeChoices.PLANNER
    service_tier = Contract.ServiceTierChoices.COMPLETA

    name = "Contrato de Assessoria Completa"
    description = "Honorários de assessoria cerimonial"
    total_amount = Decimal("6000.00")
    installments_count = 1

    status = Contract.StatusChoices.DRAFT
    signed_date = None


class SignedPlannerContractFactory(PlannerContractFactory):
    """Fábrica para contratos de assessoria assinados."""

    status = Contract.StatusChoices.SIGNED
    signed_date = factory.LazyFunction(dt.date.today)


# Aliases de compatibilidade: preservam o comportamento efetivo anterior
# (a definição PLANNER sobrescrevia a SUPPLIER). Código novo deve usar os
# nomes explícitos acima.
ContractFactory = PlannerContractFactory
SignedContractFactory = SignedPlannerContractFactory


class ContractAddendumFactory(factory.django.DjangoModelFactory):
    """Fábrica para Termos Aditivos de Contrato (ContractAddendum)."""

    class Meta:
        model = ContractAddendum

    contract = factory.SubFactory(SupplierContractFactory)
    company = factory.SelfAttribute("contract.company")
    wedding = factory.SelfAttribute("contract.wedding")

    amount = Decimal("1500.00")
    justification = factory.Faker("sentence")
    status = ContractAddendum.StatusChoices.PENDING
    signed_date = None
