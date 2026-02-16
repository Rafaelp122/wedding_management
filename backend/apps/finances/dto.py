from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from apps.core.dto import BaseDTO


@dataclass(frozen=True)
class BudgetCategoryDTO(BaseDTO):
    """Contrato de dados para categorias de orçamento."""

    planner_id: UUID
    wedding_id: UUID
    budget_id: UUID
    name: str
    allocated_budget: Decimal
    description: str = ""

    @classmethod
    def from_validated_data(
        cls, user_id: UUID, validated_data: dict
    ) -> "BudgetCategoryDTO":
        data = {**validated_data, "planner_id": user_id}
        # Mapeamento do campo slug do serializer
        if "budget" in data:
            data["budget_id"] = data.pop("budget")
        if "wedding" in data:
            data["wedding_id"] = data.pop("wedding")
        return cls.from_dict(data)


@dataclass(frozen=True)
class ExpenseDTO(BaseDTO):
    """Contrato de dados para movimentações financeiras (RF03/RF04)."""

    planner_id: UUID
    wedding_id: UUID
    category_id: UUID
    description: str
    estimated_amount: Decimal
    actual_amount: Decimal = Decimal("0.00")
    contract_id: UUID | None = None

    @classmethod
    def from_validated_data(cls, user_id: UUID, validated_data: dict) -> "ExpenseDTO":
        """Injeta o contexto do Planner logado e mapeia os dados."""
        data = {**validated_data, "planner_id": user_id}
        return cls.from_dict(data)


@dataclass(frozen=True)
class InstallmentDTO(BaseDTO):
    """Contrato de dados para parcelas individuais."""

    planner_id: UUID
    wedding_id: UUID
    expense_id: UUID
    installment_number: int
    amount: Decimal
    due_date: date
    paid_date: date | None = None
    status: str = "PENDING"
    notes: str = ""

    @classmethod
    def from_validated_data(
        cls, user_id: UUID, validated_data: dict
    ) -> "InstallmentDTO":
        # Mapeia o UUID da despesa vindo do serializer para expense_id
        return cls.from_dict({**validated_data, "planner_id": user_id})
