"""Schemas Pydantic/Ninja para a entidade de Categoria de Orçamento (BudgetCategory)."""

from decimal import Decimal
from typing import TYPE_CHECKING, cast

from ninja import Field, Schema
from pydantic import UUID4, ConfigDict


if TYPE_CHECKING:
    from apps.finances.models.budget_category import BudgetCategory


class BudgetCategoryIn(Schema):
    """Schema de entrada para criação de categoria de orçamento."""

    model_config = ConfigDict(str_strip_whitespace=True)

    budget: UUID4
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)
    allocated_budget: Decimal = Field(ge=0)


class BudgetCategoryPatchIn(Schema):
    """Schema de entrada para atualização parcial de categoria de orçamento."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)
    allocated_budget: Decimal | None = Field(default=None, ge=0)


class BudgetCategoryOut(Schema):
    """Schema de saída para exibição de categoria de orçamento."""

    uuid: UUID4
    wedding: UUID4 = Field(alias="wedding.uuid")
    budget: UUID4 = Field(alias="budget.uuid")
    name: str
    description: str | None = None
    allocated_budget: Decimal
    total_spent: Decimal = Field(default=Decimal("0.00"))

    @staticmethod
    def resolve_wedding(obj: "BudgetCategory") -> UUID4:
        """Resolve o UUID do casamento associado."""
        return obj.wedding.uuid

    @staticmethod
    def resolve_budget(obj: "BudgetCategory") -> UUID4:
        """Resolve o UUID do orçamento associado."""
        return obj.budget.uuid

    @staticmethod
    def resolve_total_spent(obj: "BudgetCategory") -> Decimal:
        """Expõe o total gasto consumindo atributo anotado ou propriedade."""
        val = getattr(obj, "_total_spent", None)
        if val is not None:
            return cast(Decimal, val)
        return obj.total_spent
