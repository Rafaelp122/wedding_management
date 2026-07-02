import datetime
import json
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ninja import Field, Schema
from pydantic import UUID4, field_validator, model_validator


if TYPE_CHECKING:
    from apps.logistics.models.contract import Contract


# ==============================================================================
# SUPPLIER SCHEMAS
# ==============================================================================
class SupplierIn(Schema):
    name: str
    cnpj: str = Field(min_length=14, max_length=18)
    phone: str
    email: str
    is_active: bool = True
    address: str = ""
    city: str = ""
    state: str = Field("", pattern="^$|^[A-Z]{2}$")
    website: str = Field("", pattern=r"^(?:https?://\S+)?$")
    notes: str = ""

    @field_validator("cnpj")
    @classmethod
    def validate_cnpj_format(cls, v: str) -> str:
        import re

        if not re.match(r"^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$", v):
            raise ValueError(
                "CNPJ deve estar no formato XX.XXX.XXX/XXXX-XX.",
            )
        return v


class SupplierPatchIn(Schema):
    name: str | None = None
    cnpj: str | None = Field(None, min_length=14, max_length=18)
    phone: str | None = None
    email: str | None = None
    is_active: bool | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = Field(None, pattern="^$|^[A-Z]{2}$")
    website: str | None = None
    notes: str | None = None

    @field_validator("cnpj")
    @classmethod
    def validate_cnpj_format(cls, v: str | None) -> str | None:
        import re

        if v is not None and not re.match(r"^(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})?$", v):
            raise ValueError(
                "CNPJ deve estar no formato XX.XXX.XXX/XXXX-XX.",
            )
        return v

    @field_validator("website")
    @classmethod
    def validate_website_format(cls, v: str | None) -> str | None:
        import re

        if v is not None and not re.match(r"^(?:https?://\S+)?$", v):
            raise ValueError("Website deve ser uma URL válida (http:// ou https://).")
        return v


class SupplierOut(Schema):
    uuid: UUID4
    name: str
    cnpj: str
    phone: str
    email: str
    is_active: bool
    address: str = ""
    city: str = ""
    state: str = Field("", min_length=0, max_length=2)
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
    pdf_file_key: str | None = None


class ContractPatchIn(Schema):
    supplier: UUID4 | None = None
    name: str | None = None
    total_amount: Decimal | None = None
    status: str | None = None
    description: str = ""
    parent: UUID4 | None = None
    pdf_file_key: str | None = None
    expiration_date: date | None = None
    alert_days_before: int | None = None


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
    alert_days_before: int | None = None
    expense_uuid: UUID4 | None = None
    parent: UUID4 | None = None
    addendums_count: int = 0
    has_file: bool = False
    file_name: str | None = None

    @staticmethod
    def resolve_expense_uuid(obj: "Contract") -> UUID4 | None:
        # Tenta pegar do annotation (Subquery)
        val = getattr(obj, "expense_id", None)
        if val is not None:
            return val

        # Fallback seguro para evitar N+1 em listas.
        # Se for uma instância isolada (ex: GET detalhe), e 'expense' estiver carregado,
        # retornamos. Se for uma lista, 'expense_id' deve ter sido anotado.

        # Em Django, para OneToOne reverso, se não for carregado via select_related,
        # acessar 'obj.expense' SEMPRE dispara uma query.

        # Para suportar o 'create_full', verificamos se 'expense' foi manualmente
        # atribuído.
        if "expense" in obj.__dict__:
            expense = obj.__dict__["expense"]
            if expense:
                return expense.uuid

        # Se estivermos em um GET detalhado (único objeto), podemos permitir a query
        # se necessário? A convenção do BOLT é NÃO fazer N+1.
        # Mas para um único objeto não é N+1.
        # No entanto, como diferenciar lista de detalhe aqui?
        # Geralmente não diferenciamos no schema.

        return None

    @staticmethod
    def resolve_supplier_name(obj: "Contract") -> str:
        val = getattr(obj, "supplier_name", None)
        if val is not None:
            return str(val)
        return obj.supplier.name

    @staticmethod
    def resolve_supplier_phone(obj: "Contract") -> str:
        val = getattr(obj, "supplier_phone", None)
        if val is not None:
            return str(val)
        return obj.supplier.phone

    @staticmethod
    def resolve_supplier_email(obj: "Contract") -> str:
        val = getattr(obj, "supplier_email", None)
        if val is not None:
            return str(val)
        return obj.supplier.email

    @staticmethod
    def resolve_has_linked_expense(obj: "Contract") -> bool:
        # Usa a annotated expense_id (disponível em list()) para evitar N+1
        if hasattr(obj, "expense_id"):
            return bool(obj.expense_id)
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
        if obj.parent_id and obj.parent:
            return obj.parent.uuid
        return None

    @staticmethod
    def resolve_addendums_count(obj: "Contract") -> int:
        val = getattr(obj, "addendums_count", None)
        if val is not None:
            return int(val)
        return obj.addendums.count()

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
    wedding: UUID4 | None = None
    contract: UUID4 | None = None
    name: str
    description: str = ""
    quantity: int = 1
    acquisition_status: str = "PENDING"


class ItemStatusTransitionIn(Schema):
    acquisition_status: str


class ItemPatchIn(Schema):
    contract: UUID4 | None = None
    name: str | None = None
    description: str = ""
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


class ContractFullCreateIn(Schema):
    wedding: UUID4
    supplier: UUID4
    name: str
    total_amount: Decimal
    status: str = "DRAFT"
    description: str = ""
    parent: UUID4 | None = None
    pdf_file_key: str | None = None

    items_data: str = "[]"

    create_expense: bool = False
    expense_category: UUID4 | None = None
    expense_num_installments: int | None = None
    expense_first_due_date: date | None = None

    @field_validator("items_data")
    def validate_items_json(cls, v: str) -> str:
        try:
            json.loads(v or "[]")
        except json.JSONDecodeError as e:
            raise ValueError("items_data deve ser um JSON válido.") from e
        return v

    @model_validator(mode="after")
    def validate_expense(self) -> "ContractFullCreateIn":
        if self.create_expense and self.expense_category is None:
            raise ValueError("Categoria é obrigatória quando create_expense é True.")
        return self


# ==============================================================================
# UPLOAD SCHEMAS
# ==============================================================================
class ContractUploadUrlIn(Schema):
    """Schema de entrada para requisição de URL de upload pré-assinada."""

    filename: str
    wedding_id: UUID4


class ContractUploadUrlOut(Schema):
    """Schema de saída com URL pré-assinada e chave do objeto no R2/S3."""

    upload_url: str
    object_key: str


class ContractUploadIn(Schema):
    """Schema de entrada para associar a chave do arquivo enviado."""

    pdf_file_key: str
