import datetime
from datetime import date
from decimal import Decimal

from ninja import Field, Schema
from pydantic import UUID4


# ==============================================================================
# SUPPLIER SCHEMAS
# ==============================================================================
class SupplierIn(Schema):
    name: str
    cnpj: str
    phone: str
    email: str
    is_active: bool = True


class SupplierPatchIn(Schema):
    name: str | None = None
    cnpj: str | None = None
    phone: str | None = None
    email: str | None = None
    is_active: bool | None = None


class SupplierOut(Schema):
    uuid: UUID4
    name: str
    cnpj: str
    phone: str
    email: str
    is_active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime


# ==============================================================================
# CONTRACT SCHEMAS
# ==============================================================================
class ContractIn(Schema):
    event: UUID4
    supplier: UUID4
    budget_category: UUID4
    total_amount: Decimal
    status: str = "DRAFT"
    description: str = ""


class ContractPatchIn(Schema):
    event: UUID4 | None = None
    supplier: UUID4 | None = None
    budget_category: UUID4 | None = None
    total_amount: Decimal | None = None
    status: str | None = None


class ContractOut(Schema):
    uuid: UUID4
    event: UUID4 = Field(alias="event.uuid")
    supplier: UUID4 = Field(alias="supplier.uuid")
    budget_category: UUID4 | None = Field(None, alias="budget_category.uuid")
    total_amount: Decimal
    status: str
    description: str
    expiration_date: date | None = None
    signed_date: date | None = None
    created_at: datetime.datetime
    updated_at: datetime.datetime


# ==============================================================================
# ITEM SCHEMAS
# ==============================================================================
class ItemIn(Schema):
    event: UUID4
    contract: UUID4 | None = None
    name: str
    description: str = ""
    quantity: int = 1


class ItemPatchIn(Schema):
    event: UUID4 | None = None
    contract: UUID4 | None = None
    name: str | None = None
    description: str | None = None
    quantity: int | None = None


class ItemOut(Schema):
    uuid: UUID4
    event: UUID4 = Field(alias="event.uuid")
    contract: UUID4 | None = Field(None, alias="contract.uuid")
    name: str
    description: str
    quantity: int
    acquisition_status: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
