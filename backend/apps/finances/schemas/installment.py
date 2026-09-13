"""Schemas Pydantic/Ninja para a entidade de Parcela (Installment)."""

from datetime import date
from decimal import Decimal
from typing import Any, cast

from ninja import Field, Schema
from pydantic import UUID4, ConfigDict


class InstallmentIn(Schema):
    """Schema de entrada para criação de parcela."""

    model_config = ConfigDict(str_strip_whitespace=True)

    expense: UUID4
    installment_number: int = Field(gt=0)
    amount: Decimal = Field(ge=0)
    due_date: date
    paid_date: date | None = None
    notes: str = Field(default="", max_length=500)


class InstallmentPatchIn(Schema):
    """Schema de entrada para atualização parcial de parcela."""

    model_config = ConfigDict(str_strip_whitespace=True)

    installment_number: int | None = Field(default=None, gt=0)
    amount: Decimal | None = Field(default=None, ge=0)
    due_date: date | None = None
    paid_date: date | None = None
    notes: str = Field(default="", max_length=500)


class InstallmentAdjustIn(Schema):
    """Schema de entrada para ajuste financeiro de parcela."""

    model_config = ConfigDict(str_strip_whitespace=True)

    amount: Decimal | None = Field(default=None, ge=0)
    due_date: date | None = None


class InstallmentOut(Schema):
    """Schema de saída para exibição de parcela."""

    uuid: UUID4
    wedding: UUID4 = Field(alias="wedding.uuid")
    expense: UUID4 = Field(alias="expense.uuid")
    installment_number: int
    amount: Decimal
    due_date: date
    paid_date: date | None = None
    status: str
    notes: str | None = None

    @staticmethod
    def resolve_wedding(obj: Any) -> UUID4:
        """Resolve o UUID do casamento."""
        return cast(UUID4, obj.wedding.uuid)

    @staticmethod
    def resolve_expense(obj: Any) -> UUID4:
        """Resolve o UUID da despesa."""
        return cast(UUID4, obj.expense.uuid)
