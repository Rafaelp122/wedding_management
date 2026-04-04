import datetime
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
    wedding: UUID4
    supplier: UUID4
    total_amount: Decimal
    status: str


class ContractPatchIn(Schema):
    wedding: UUID4 | None = None
    supplier: UUID4 | None = None
    total_amount: Decimal | None = None
    status: str | None = None


class ContractOut(Schema):
    uuid: UUID4
    # Dot notation is native to Django Ninja schemas for extracting attributes
    wedding: UUID4 = Field(alias="wedding.uuid")
    supplier: UUID4 = Field(alias="supplier.uuid")
    total_amount: Decimal
    status: str
    created_at: datetime.datetime
    updated_at: datetime.datetime


# ==============================================================================
# ITEM SCHEMAS
# ==============================================================================
class ItemIn(Schema):
    wedding: UUID4
    budget_category: UUID4
    contract: UUID4 | None = None
    name: str
    quantity: int


class ItemPatchIn(Schema):
    wedding: UUID4 | None = None
    budget_category: UUID4 | None = None
    contract: UUID4 | None = None
    name: str | None = None
    quantity: int | None = None


class ItemOut(Schema):
    uuid: UUID4
    wedding: UUID4 = Field(alias="wedding.uuid")
    budget_category: UUID4 = Field(alias="budget_category.uuid")
    contract: UUID4 | None = Field(None, alias="contract.uuid")
    name: str
    quantity: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
