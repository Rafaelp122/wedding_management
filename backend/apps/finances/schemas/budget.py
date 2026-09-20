"""Schemas Pydantic/Ninja para a entidade de Orçamento (Budget)."""

from decimal import Decimal
from typing import TYPE_CHECKING, Any, cast

from ninja import Field, Schema
from pydantic import UUID4, ConfigDict


if TYPE_CHECKING:
    from apps.finances.models.budget import Budget


class BudgetIn(Schema):
    """Schema de entrada para criação de orçamento."""

    model_config = ConfigDict(str_strip_whitespace=True)

    wedding: UUID4
    total_estimated: Decimal = Field(ge=0)
    notes: str = Field(default="", max_length=1000)


class BudgetPatchIn(Schema):
    """Schema de entrada para atualização parcial de orçamento."""

    model_config = ConfigDict(str_strip_whitespace=True)

    total_estimated: Decimal | None = Field(default=None, ge=0)
    notes: str = Field(default="", max_length=1000)


class BudgetOut(Schema):
    """Schema de saída para exibição de orçamento."""

    uuid: UUID4
    wedding: UUID4 = Field(alias="wedding.uuid")
    total_estimated: Decimal
    total_overall_spent: Decimal = Field(default=Decimal("0.00"))
    total_allocated: Decimal = Field(default=Decimal("0.00"))
    unallocated_budget: Decimal = Field(default=Decimal("0.00"))
    tenant_average_budget: Decimal | None = None
    comparison_percentage: float | None = None
    notes: str | None = None

    @staticmethod
    def resolve_tenant_average_budget(obj: Any) -> Decimal | None:
        """Resolve a média do orçamento dos casamentos do tenant."""
        val = getattr(obj, "_tenant_average_budget", None)
        if val is not None:
            return Decimal(str(val)) if not isinstance(val, Decimal) else val
        return None

    @staticmethod
    def resolve_comparison_percentage(obj: Any) -> float | None:
        """Resolve o percentual de comparação com a média do tenant."""
        val = getattr(obj, "_comparison_percentage", None)
        if val is not None:
            return float(val)
        return None

    @staticmethod
    def resolve_wedding(obj: "Budget") -> UUID4:
        """Resolve o UUID do casamento associado."""
        return obj.wedding.uuid

    @staticmethod
    def resolve_total_overall_spent(obj: "Budget") -> Decimal:
        """Expõe o total gasto acumulado consumindo anotação ou propriedade."""
        val = getattr(obj, "_total_overall_spent", None)
        if val is not None:
            return cast(Decimal, val)
        return obj.total_overall_spent

    @staticmethod
    def resolve_total_allocated(obj: Any) -> Decimal:
        """Resolve a verba total alocada consumindo atributo ou propriedade."""
        val = getattr(obj, "_total_allocated", None)
        if val is not None:
            return cast(Decimal, val)
        val = getattr(obj, "total_allocated", None)
        if val is not None:
            return cast(Decimal, val)
        return Decimal("0.00")

    @staticmethod
    def resolve_unallocated_budget(obj: Any) -> Decimal:
        """Resolve a verba ainda não alocada consumindo atributo ou propriedade."""
        val = getattr(obj, "unallocated_budget", None)
        if val is not None:
            return cast(Decimal, val)
        allocated = BudgetOut.resolve_total_allocated(obj)
        total_estimated = getattr(obj, "total_estimated", Decimal("0.00")) or Decimal(
            "0.00"
        )
        return max(Decimal("0.00"), total_estimated - allocated)
