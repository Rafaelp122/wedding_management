"""Fábricas do domínio de Fornecedores (apps.suppliers)."""

from __future__ import annotations

import factory

from apps.suppliers.models import Supplier


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
