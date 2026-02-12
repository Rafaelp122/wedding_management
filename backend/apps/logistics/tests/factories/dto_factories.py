from datetime import date
from decimal import Decimal

import factory

from apps.logistics.dto import ContractDTO, ItemDTO, SupplierDTO


class SupplierDTOFactory(factory.Factory):
    """Fábrica para gerar DTOs de Supplier em memória."""

    class Meta:
        model = SupplierDTO

    name = factory.Faker("company")
    cnpj = factory.LazyAttribute(lambda _: "00.000.000/0001-00")
    phone = factory.Faker("phone_number")
    email = factory.Faker("company_email")
    website = factory.Faker("url")
    address = factory.Faker("street_address")
    city = factory.Faker("city")
    state = factory.Faker("state_abbr")
    notes = factory.Faker("sentence")
    is_active = True
    planner_id = factory.Faker("uuid4")


class ContractDTOFactory(factory.Factory):
    """Fábrica de DTO para Contratos em memória."""

    class Meta:
        model = ContractDTO

    wedding_id = factory.Faker("uuid4")
    supplier_id = factory.Faker("uuid4")
    total_amount = factory.LazyAttribute(lambda _: Decimal("5000.00"))
    description = factory.Faker("paragraph")
    status = "DRAFT"
    expiration_date = factory.LazyFunction(lambda: date(2026, 12, 31))
    alert_days_before = 30
    signed_date = None
    pdf_file = None
    planner_id = factory.Faker("uuid4")


class ItemDTOFactory(factory.Factory):
    """Fábrica de DTO para Itens de Logística em memória."""

    class Meta:
        model = ItemDTO

    wedding_id = factory.Faker("uuid4")
    budget_category_id = factory.Faker("uuid4")
    contract_id = factory.Faker("uuid4")
    name = factory.Faker("word")
    description = factory.Faker("sentence")
    quantity = 1
    acquisition_status = "PENDING"
    planner_id = factory.Faker("uuid4")
