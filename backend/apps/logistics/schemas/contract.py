"""Schemas Pydantic/Ninja para a entidade de Contrato (Contract)."""

import datetime
import json
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, cast

from ninja import Field, Schema
from pydantic import UUID4, ConfigDict, field_validator, model_validator


if TYPE_CHECKING:
    from apps.logistics.models.contract import Contract


class ContractIn(Schema):
    """Schema de entrada para criação de contrato."""

    model_config = ConfigDict(str_strip_whitespace=True)

    wedding: UUID4
    supplier: UUID4
    name: str = Field(min_length=1, max_length=255)
    total_amount: Decimal = Field(ge=0)
    status: str = "DRAFT"
    description: str = ""
    parent: UUID4 | None = None
    pdf_file_key: str | None = None


class ContractPatchIn(Schema):
    """Schema de entrada para atualização parcial de contrato."""

    model_config = ConfigDict(str_strip_whitespace=True)

    supplier: UUID4 | None = None
    name: str | None = Field(default=None, min_length=1, max_length=255)
    total_amount: Decimal | None = Field(default=None, ge=0)
    status: str | None = None
    description: str = ""
    parent: UUID4 | None = None
    pdf_file_key: str | None = None
    expiration_date: date | None = None
    alert_days_before: int | None = None


class ContractStatusTransitionIn(Schema):
    """Schema de entrada para transição de status de contrato."""

    model_config = ConfigDict(str_strip_whitespace=True)

    status: str = Field(min_length=1)


class ContractOut(Schema):
    """Schema de saída para exibição de contrato."""

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
    addendums_total_amount: Decimal = Decimal("0.00")
    total_amount_with_addendums: Decimal = Decimal("0.00")
    has_file: bool = False
    file_name: str | None = None

    @staticmethod
    def resolve_expense_uuid(obj: "Contract") -> UUID4 | None:
        """Resolve o UUID da despesa vinculada se existente no cache ou anotada."""
        val = getattr(obj, "expense_id", None)
        if val:
            return cast("UUID4 | None", val)
        fields_cache = getattr(getattr(obj, "_state", None), "fields_cache", {})
        expense = fields_cache.get("expense")
        return expense.uuid if expense else None

    @staticmethod
    def resolve_supplier_name(obj: "Contract") -> str:
        """Resolve o nome do fornecedor a partir de atributo anotado ou relação."""
        val = getattr(obj, "supplier_name", None)
        if val is not None:
            return str(val)
        return obj.supplier.name if hasattr(obj, "supplier") and obj.supplier else ""

    @staticmethod
    def resolve_supplier_phone(obj: "Contract") -> str:
        """Resolve o telefone do fornecedor a partir de atributo anotado ou relação."""
        val = getattr(obj, "supplier_phone", None)
        if val is not None:
            return str(val)
        return obj.supplier.phone if hasattr(obj, "supplier") and obj.supplier else ""

    @staticmethod
    def resolve_supplier_email(obj: "Contract") -> str:
        """Resolve o e-mail do fornecedor a partir de atributo anotado ou relação."""
        val = getattr(obj, "supplier_email", None)
        if val is not None:
            return str(val)
        return obj.supplier.email if hasattr(obj, "supplier") and obj.supplier else ""

    @staticmethod
    def resolve_has_linked_expense(obj: "Contract") -> bool:
        """Verifica se há despesa financeira associada ao contrato."""
        if getattr(obj, "expense_id", None):
            return True
        fields_cache = getattr(getattr(obj, "_state", None), "fields_cache", {})
        return bool(fields_cache.get("expense"))

    @staticmethod
    def resolve_progress_percent(obj: "Contract") -> int:
        """Calcula o percentual de progresso de pagamento do contrato."""
        total_paid = getattr(obj, "total_paid", None)
        if total_paid is not None and obj.total_amount:
            return int(total_paid / obj.total_amount * 100)
        return 0

    @staticmethod
    def resolve_parent(obj: "Contract") -> UUID4 | None:
        """Resolve o UUID do contrato pai no caso de aditivo."""
        if obj.parent:
            return obj.parent.uuid
        return None

    @staticmethod
    def resolve_addendums_count(obj: "Contract") -> int:
        """Resolve a contagem de aditivos ativos a partir de anotação na QuerySet."""
        val = getattr(obj, "addendums_count", None)
        return int(val) if val is not None else 0

    @staticmethod
    def resolve_addendums_total_amount(obj: "Contract") -> Decimal:
        """Calcula o montante total de aditivos a partir de anotação na QuerySet."""
        val = getattr(obj, "addendums_total_amount", None)
        return Decimal(str(val)) if val is not None else Decimal("0.00")

    @staticmethod
    def resolve_total_amount_with_addendums(obj: "Contract") -> Decimal:
        """Calcula o valor total consolidado do contrato incluindo aditivos."""
        addendums_val = getattr(obj, "addendums_total_amount", None)
        base = obj.total_amount or Decimal("0.00")
        if addendums_val is not None:
            return base + Decimal(str(addendums_val))
        return base

    @staticmethod
    def resolve_supplier(obj: "Contract") -> UUID4:
        """Resolve o UUID do fornecedor associado."""
        return obj.supplier.uuid

    @staticmethod
    def resolve_has_file(obj: "Contract") -> bool:
        """Indica se há arquivo PDF anexado."""
        return obj.has_file

    @staticmethod
    def resolve_file_name(obj: "Contract") -> str | None:
        """Retorna o nome do arquivo PDF anexado."""
        return obj.file_name


class ContractFullCreateIn(Schema):
    """Schema de entrada para criação de contrato com itens e despesa opcional."""

    model_config = ConfigDict(str_strip_whitespace=True)

    wedding: UUID4
    supplier: UUID4
    name: str = Field(min_length=1, max_length=255)
    total_amount: Decimal = Field(ge=0)
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
    @classmethod
    def validate_items_json(cls, v: str) -> str:
        """Valida se items_data é um JSON decodificável."""
        try:
            json.loads(v or "[]")
        except json.JSONDecodeError as e:
            raise ValueError("items_data deve ser um JSON válido.") from e
        return v

    @model_validator(mode="after")
    def validate_expense(self) -> "ContractFullCreateIn":
        """Valida se a categoria foi informada quando create_expense é True."""
        if self.create_expense and self.expense_category is None:
            raise ValueError("Categoria é obrigatória quando create_expense é True.")
        return self


class ContractUploadUrlIn(Schema):
    """Schema de entrada para requisição de URL de upload pré-assinada."""

    model_config = ConfigDict(str_strip_whitespace=True)

    filename: str
    wedding_id: UUID4


class ContractUploadUrlOut(Schema):
    """Schema de saída com URL pré-assinada e chave do objeto no R2/S3."""

    upload_url: str
    object_key: str


class ContractUploadIn(Schema):
    """Schema de entrada para associar a chave do arquivo enviado."""

    model_config = ConfigDict(str_strip_whitespace=True)

    pdf_file_key: str
