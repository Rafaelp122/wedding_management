"""
Schemas Pydantic/Ninja para a entidade unificada de Contrato (Contract).
"""

from __future__ import annotations

import datetime
import json
from datetime import date
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING, Any, cast

from ninja import Field, Schema
from pydantic import UUID4, ConfigDict, field_validator, model_validator

from apps.contracts.schemas.contract_addendum import (
    ContractAddendumOut,
)
from apps.logistics.schemas.item import ItemOut


if TYPE_CHECKING:
    from apps.contracts.models.contract import Contract


class ContractTypeEnum(StrEnum):
    PLANNER = "PLANNER"
    SUPPLIER = "SUPPLIER"


class ServiceTierEnum(StrEnum):
    COMPLETA = "COMPLETA"
    PARCIAL = "PARCIAL"
    FINAL = "FINAL"


class ContractStatusEnum(StrEnum):
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    SIGNED = "SIGNED"
    CANCELED = "CANCELED"


class ContractItemIn(Schema):
    """Schema de entrada para item de suprimento associado ao contrato."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=255)
    quantity: int = Field(gt=0, default=1)
    description: str = ""
    unit_price: Decimal | None = None


class ContractItemOut(Schema):
    """Schema de saída para item de suprimento associado ao contrato."""

    uuid: UUID4
    name: str
    quantity: int
    description: str = ""
    status: str = "PENDING"


class ContractIn(Schema):
    """Schema de entrada para criação de contrato."""

    model_config = ConfigDict(str_strip_whitespace=True)

    wedding: UUID4
    contract_type: str = ContractTypeEnum.SUPPLIER
    service_tier: str | None = None
    supplier: UUID4 | None = None
    client: UUID4 | None = None
    name: str = Field(min_length=1, max_length=255)
    total_amount: Decimal = Field(ge=0)
    status: str = "DRAFT"
    description: str = ""
    installments_count: int = Field(default=1, ge=1)
    expiration_date: date | None = None
    alert_days_before: int = 30
    signed_date: date | None = None
    parent: UUID4 | None = None
    pdf_file_key: str | None = None


class ContractPatchIn(Schema):
    """Schema de entrada para atualização parcial de contrato."""

    model_config = ConfigDict(str_strip_whitespace=True)

    contract_type: str | None = None
    service_tier: str | None = None
    supplier: UUID4 | None = None
    client: UUID4 | None = None
    name: str | None = Field(default=None, min_length=1, max_length=255)
    total_amount: Decimal | None = Field(default=None, ge=0)
    installments_count: int | None = Field(default=None, ge=1)
    status: str | None = None
    description: str = ""
    parent: UUID4 | None = None
    pdf_file_key: str | None = None
    expiration_date: date | None = None
    alert_days_before: int | None = None
    signed_date: date | None = None


class ContractStatusTransitionIn(Schema):
    """Schema de entrada para transição de status de contrato."""

    model_config = ConfigDict(str_strip_whitespace=True)

    status: str = Field(min_length=1)


class ContractOut(Schema):
    """Schema de saída para exibição de contrato."""

    uuid: UUID4
    wedding: UUID4 = Field(alias="wedding.uuid")
    contract_type: str = "SUPPLIER"
    service_tier: str | None = None
    supplier: UUID4 | None = None
    client: UUID4 | None = None
    name: str = ""
    total_amount: Decimal
    installments_count: int = 1
    status: str
    description: str = ""
    expiration_date: date | None = None
    signed_date: date | None = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    supplier_name: str = ""
    supplier_phone: str = ""
    supplier_email: str = ""
    client_name: str = ""
    has_linked_expense: bool = False
    progress_percent: int = 0
    alert_days_before: int | None = None
    expense_uuid: UUID4 | None = None
    parent: UUID4 | None = None
    addendums_count: int = 0
    addendums_total_amount: Decimal = Decimal("0.00")
    total_amount_with_addendums: Decimal = Decimal("0.00")
    base_amount: Decimal = Decimal("0.00")
    addendums_total: Decimal = Decimal("0.00")
    effective_amount: Decimal = Decimal("0.00")
    addendums: list[ContractAddendumOut] = Field(default_factory=list)
    has_file: bool = False
    file_name: str | None = None
    is_addendum: bool = False
    allowed_transitions: list[str] = Field(default_factory=list)

    @staticmethod
    def resolve_supplier(obj: Contract) -> UUID4 | None:
        """Resolve o UUID do fornecedor associado, se houver."""
        if hasattr(obj, "supplier") and obj.supplier:
            return obj.supplier.uuid
        return None

    @staticmethod
    def resolve_client(obj: Contract) -> UUID4 | None:
        """Resolve o UUID do cliente associado, se houver."""
        if hasattr(obj, "client") and obj.client:
            return obj.client.uuid
        return None

    @staticmethod
    def resolve_client_name(obj: Contract) -> str:
        """Resolve o nome do cliente a partir de atributo anotado ou relação."""
        val = getattr(obj, "client_name", None)
        if val is not None:
            return str(val)
        return obj.client.name if hasattr(obj, "client") and obj.client else ""

    @staticmethod
    def resolve_expense_uuid(obj: Contract) -> UUID4 | None:
        """Resolve o UUID da despesa vinculada se existente no cache ou anotada."""
        val = getattr(obj, "expense_id", None)
        if val:
            return cast("UUID4 | None", val)
        fields_cache = getattr(getattr(obj, "_state", None), "fields_cache", {})
        expense = fields_cache.get("expense")
        return expense.uuid if expense else None

    @staticmethod
    def resolve_supplier_name(obj: Contract) -> str:
        """Resolve o nome do fornecedor a partir de atributo anotado ou relação."""
        val = getattr(obj, "supplier_name", None)
        if val is not None:
            return str(val)
        return obj.supplier.name if hasattr(obj, "supplier") and obj.supplier else ""

    @staticmethod
    def resolve_supplier_phone(obj: Contract) -> str:
        """Resolve o telefone do fornecedor a partir de atributo anotado ou relação."""
        val = getattr(obj, "supplier_phone", None)
        if val is not None:
            return str(val)
        return obj.supplier.phone if hasattr(obj, "supplier") and obj.supplier else ""

    @staticmethod
    def resolve_supplier_email(obj: Contract) -> str:
        """Resolve o e-mail do fornecedor a partir de atributo anotado ou relação."""
        val = getattr(obj, "supplier_email", None)
        if val is not None:
            return str(val)
        return obj.supplier.email if hasattr(obj, "supplier") and obj.supplier else ""

    @staticmethod
    def resolve_has_linked_expense(obj: Contract) -> bool:
        """Verifica se há despesa financeira associada ao contrato."""
        if getattr(obj, "expense_id", None):
            return True
        fields_cache = getattr(getattr(obj, "_state", None), "fields_cache", {})
        return bool(fields_cache.get("expense"))

    @staticmethod
    def resolve_progress_percent(obj: Contract) -> int:
        """Calcula o percentual de progresso de pagamento do contrato."""
        total_paid = getattr(obj, "total_paid", None)
        if total_paid is not None and obj.total_amount:
            return int(total_paid / obj.total_amount * 100)
        return 0

    @staticmethod
    def resolve_parent(obj: Contract) -> UUID4 | None:
        """Resolve o UUID do contrato pai no caso de aditivo."""
        return None

    @staticmethod
    def resolve_addendums_count(obj: Contract) -> int:
        """Resolve a contagem de aditivos ativos a partir de anotação na QuerySet."""
        val = getattr(obj, "addendums_count", None)
        return int(val) if val is not None else 0

    @staticmethod
    def resolve_addendums_total_amount(obj: Contract) -> Decimal:
        """Calcula o montante total de aditivos a partir de anotação na QuerySet."""
        val = getattr(obj, "addendums_total_amount", None)
        if val is not None:
            return Decimal(str(val))
        return getattr(obj, "addendums_total", Decimal("0.00"))

    @staticmethod
    def resolve_total_amount_with_addendums(obj: Contract) -> Decimal:
        """Calcula o valor total consolidado do contrato incluindo aditivos."""
        val = getattr(obj, "effective_amount", None)
        if val is not None:
            return Decimal(str(val))
        return obj.base_amount + obj.addendums_total

    @staticmethod
    def resolve_base_amount(obj: Contract) -> Decimal:
        """Retorna o valor de face original do contrato."""
        return getattr(obj, "base_amount", obj.total_amount or Decimal("0.00"))

    @staticmethod
    def resolve_addendums_total(obj: Contract) -> Decimal:
        """Retorna a soma de aditivos assinados."""
        val = getattr(obj, "addendums_total", None)
        if val is not None:
            return Decimal(str(val))
        return getattr(obj, "addendums_total_amount", Decimal("0.00"))

    @staticmethod
    def resolve_effective_amount(obj: Contract) -> Decimal:
        """Retorna o valor efetivo consolidado."""
        val = getattr(obj, "effective_amount", None)
        if val is not None:
            return Decimal(str(val))
        return obj.base_amount + obj.addendums_total

    @staticmethod
    def resolve_addendums(obj: Contract) -> list[Any]:
        """Resolve a lista de aditivos vinculados."""
        if (
            hasattr(obj, "_prefetched_objects_cache")
            and "addendums" in obj._prefetched_objects_cache
        ):
            return list(obj.addendums.all())
        if hasattr(obj, "addendums"):
            return list(obj.addendums.all())
        return []

    @staticmethod
    def resolve_has_file(obj: Contract) -> bool:
        """Indica se há arquivo PDF anexado."""
        return obj.has_file

    @staticmethod
    def resolve_file_name(obj: Contract) -> str | None:
        """Retorna o nome do arquivo PDF anexado."""
        return obj.file_name

    @staticmethod
    def resolve_is_addendum(obj: Contract) -> bool:
        """Indica se este contrato é um termo aditivo (sempre False para Contract)."""
        return False

    @staticmethod
    def resolve_allowed_transitions(obj: Contract) -> list[str]:
        """Resolve as transições de status permitidas para o contrato."""
        allowed_dict = (
            getattr(obj, "PLANNER_ALLOWED_TRANSITIONS", obj.ALLOWED_TRANSITIONS)
            if getattr(obj, "contract_type", None) == "PLANNER"
            else obj.ALLOWED_TRANSITIONS
        )
        return [
            t.value if hasattr(t, "value") else str(t)
            for t in allowed_dict.get(obj.status, [])
        ]


class ContractDetailAggregateOut(Schema):
    """Schema de saída agregado com contrato, itens e aditivos."""

    contract: ContractOut
    items: list[ItemOut]
    addendums: list[ContractAddendumOut]


class ContractSignIn(Schema):
    """Schema de entrada para formalização de assinatura de contrato."""

    model_config = ConfigDict(str_strip_whitespace=True)

    signed_date: date | None = None
    pdf_file_key: str | None = None


class ContractFullCreateIn(Schema):
    """Schema de entrada para criação de contrato com itens e despesa opcional."""

    model_config = ConfigDict(str_strip_whitespace=True)

    wedding: UUID4
    contract_type: str = ContractTypeEnum.SUPPLIER
    service_tier: str | None = None
    supplier: UUID4 | None = None
    client: UUID4 | None = None
    name: str = Field(min_length=1, max_length=255)
    total_amount: Decimal = Field(ge=0)
    installments_count: int = Field(default=1, ge=1)
    status: str = "DRAFT"
    description: str = ""
    parent: UUID4 | None = None
    pdf_file_key: str | None = None

    items: list[Any] = Field(default_factory=list)
    items_data: str | None = None

    create_expense: bool = False
    expense_category: UUID4 | None = None
    expense_num_installments: int | None = None
    expense_first_due_date: date | None = None

    @field_validator("items_data")
    @classmethod
    def validate_items_json(cls, v: str | None) -> str | None:
        """Valida se items_data é um JSON decodificável."""
        if v is None:
            return None
        try:
            json.loads(v or "[]")
        except json.JSONDecodeError as e:
            raise ValueError("items_data deve ser um JSON válido.") from e
        return v

    @model_validator(mode="after")
    def validate_expense(self) -> ContractFullCreateIn:
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
