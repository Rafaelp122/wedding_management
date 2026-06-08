import datetime
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ninja import Field, Schema
from pydantic import UUID4


if TYPE_CHECKING:
    from apps.logistics.models.contract import Contract


# ==============================================================================
# SUPPLIER SCHEMAS
# ==============================================================================
class SupplierIn(Schema):
    name: str
    cnpj: str
    phone: str
    email: str
    is_active: bool = True
    address: str = ""
    city: str = ""
    state: str = Field("", max_length=2)
    website: str = Field("", pattern=r"^(?:https?://\S+)?$")
    notes: str = ""


class SupplierPatchIn(Schema):
    name: str | None = None
    cnpj: str | None = None
    phone: str | None = None
    email: str | None = None
    is_active: bool | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = Field(None, max_length=2)
    website: str = ""
    notes: str | None = None


class SupplierOut(Schema):
    uuid: UUID4
    name: str
    cnpj: str
    phone: str
    email: str
    is_active: bool
    address: str = ""
    city: str = ""
    state: str = Field("", max_length=2)
    website: str = ""
    notes: str = ""
    created_at: datetime.datetime
    updated_at: datetime.datetime


# ==============================================================================
# CONTRACT SCHEMAS
# ==============================================================================
class ContractIn(Schema):
    wedding: UUID4
    supplier: UUID4
    name: str
    total_amount: Decimal
    status: str = "DRAFT"
    description: str = ""
    parent: UUID4 | None = None


class ContractPatchIn(Schema):
    wedding: UUID4 | None = None
    supplier: UUID4 | None = None
    name: str | None = None
    total_amount: Decimal | None = None
    status: str | None = None
    description: str | None = None
    parent: UUID4 | None = None


class ContractStatusTransitionIn(Schema):
    status: str


class ContractOut(Schema):
    uuid: UUID4
    wedding: UUID4 = Field(alias="wedding.uuid")
    supplier: UUID4 = Field(alias="supplier.uuid")
    name: str = ""
    total_amount: Decimal
    status: str
    description: str = ""
    expiration_date: date | None = None
    signed_date: date | None = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    supplier_name: str = ""
    supplier_phone: str = ""
    supplier_email: str = ""
    has_linked_expense: bool = False
    progress_percent: int = 0
    expense_uuid: UUID4 | None = None
    parent: UUID4 | None = None
    addendums_count: int = 0
    has_file: bool = False
    file_name: str | None = None

    @staticmethod
    def resolve_expense_uuid(obj: "Contract") -> UUID4 | None:
        annotated = getattr(obj, "expense_id", None)
        if annotated:
            return annotated
        if hasattr(obj, "expense") and obj.expense:
            return obj.expense.uuid
        return None

    @staticmethod
    def resolve_supplier_name(obj: "Contract") -> str:
        return getattr(obj, "supplier_name", obj.supplier.name)

    @staticmethod
    def resolve_supplier_phone(obj: "Contract") -> str:
        return getattr(obj, "supplier_phone", obj.supplier.phone)

    @staticmethod
    def resolve_supplier_email(obj: "Contract") -> str:
        return getattr(obj, "supplier_email", obj.supplier.email)

    @staticmethod
    def resolve_has_linked_expense(obj: "Contract") -> bool:
        # Usa a annotated expense_id (disponível em list()) para evitar N+1
        expense_id = getattr(obj, "expense_id", None)
        if expense_id:
            return True
        # Fallback para get() que carrega expense via select_related
        return hasattr(obj, "expense") and obj.expense is not None

    @staticmethod
    def resolve_progress_percent(obj: "Contract") -> int:
        total_paid = getattr(obj, "total_paid", None)
        if total_paid is not None and obj.total_amount:
            return int(total_paid / obj.total_amount * 100)
        return 0

    @staticmethod
    def resolve_parent(obj: "Contract") -> UUID4 | None:
        if obj.parent:
            return obj.parent.uuid
        return None

    @staticmethod
    def resolve_addendums_count(obj: "Contract") -> int:
        return getattr(obj, "addendums_count", obj.addendums.count())

    @staticmethod
    def resolve_supplier(obj: "Contract") -> UUID4:
        return obj.supplier.uuid

    @staticmethod
    def resolve_has_file(obj: "Contract") -> bool:
        return bool(obj.pdf_file)

    @staticmethod
    def resolve_file_name(obj: "Contract") -> str | None:
        if obj.pdf_file:
            return obj.pdf_file.name.split("/")[-1]
        return None


# ==============================================================================
# ITEM SCHEMAS
# ==============================================================================
class ItemIn(Schema):
    wedding: UUID4
    contract: UUID4 | None = None
    name: str
    description: str = ""
    quantity: int = 1
    acquisition_status: str = "PENDING"


class ItemStatusTransitionIn(Schema):
    acquisition_status: str


class ItemPatchIn(Schema):
    wedding: UUID4 | None = None
    contract: UUID4 | None = None
    name: str | None = None
    description: str | None = None
    quantity: int | None = None
    acquisition_status: str | None = None


class ItemOut(Schema):
    uuid: UUID4
    wedding: UUID4 = Field(alias="wedding.uuid")
    contract: UUID4 | None = Field(None, alias="contract.uuid")
    name: str
    description: str
    quantity: int
    acquisition_status: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
