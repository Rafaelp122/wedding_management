from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import AliasChoices, Field

from apps.core.dto import BaseDTO


class BudgetCategoryDTO(BaseDTO):
    """
    Contrato de dados para categorias de orçamento.
    Utiliza aliases para mapear campos do Serializer (slugs) para IDs internos.
    """

    planner_id: UUID
    name: str
    allocated_budget: Decimal
    description: str = ""

    # Mapeia 'budget' ou 'budget_id' para o atributo budget_id
    budget_id: UUID = Field(validation_alias=AliasChoices("budget_id", "budget"))
    # Mapeia 'wedding' ou 'wedding_id' para o atributo wedding_id
    wedding_id: UUID = Field(validation_alias=AliasChoices("wedding_id", "wedding"))


class ExpenseDTO(BaseDTO):
    """
    Contrato de dados para movimentações financeiras (RF03/RF04).
    """

    planner_id: UUID
    wedding_id: UUID
    description: str
    estimated_amount: Decimal
    actual_amount: Decimal = Decimal("0.00")
    contract_id: UUID | None = None

    # Mapeia 'category' vindo do serializer para o category_id interno
    category_id: UUID = Field(validation_alias=AliasChoices("category_id", "category"))


class InstallmentDTO(BaseDTO):
    """
    Contrato de dados para parcelas individuais.
    """

    planner_id: UUID
    wedding_id: UUID
    installment_number: int
    amount: Decimal
    due_date: date
    paid_date: date | None = None
    status: str = "PENDING"
    notes: str = ""

    # Mapeia 'expense' vindo do serializer para o expense_id interno
    expense_id: UUID = Field(validation_alias=AliasChoices("expense_id", "expense"))
