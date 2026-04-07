from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ninja import Schema
from pydantic import UUID4, Field


if TYPE_CHECKING:
    from apps.finances.models.expense import Expense


# --- BUDGET SCHEMAS ---
class BudgetIn(Schema):
    wedding: UUID4
    total_estimated: Decimal
    notes: str | None = None


class BudgetPatchIn(Schema):
    total_estimated: Decimal | None = None
    notes: str | None = None


class BudgetOut(Schema):
    uuid: UUID4
    wedding: UUID4 = Field(alias="wedding.uuid")
    total_estimated: Decimal
    notes: str | None = None


# --- BUDGET CATEGORY SCHEMAS ---
class BudgetCategoryIn(Schema):
    budget: UUID4
    name: str = Field(..., max_length=255)
    description: str | None = None
    allocated_budget: Decimal


class BudgetCategoryPatchIn(Schema):
    name: str | None = Field(None, max_length=255)
    description: str | None = None
    allocated_budget: Decimal | None = None


class BudgetCategoryOut(Schema):
    uuid: UUID4
    wedding: UUID4 = Field(
        alias="wedding.uuid"
    )  # Read-Only logic keeps it in the output
    budget: UUID4 = Field(alias="budget.uuid")
    name: str
    description: str | None = None
    allocated_budget: Decimal


# --- EXPENSE SCHEMAS ---
class ExpenseIn(Schema):
    category: UUID4
    contract: UUID4 | None = None
    description: str = Field(..., max_length=255)
    estimated_amount: Decimal
    actual_amount: Decimal


class ExpensePatchIn(Schema):
    category: UUID4 | None = None
    contract: UUID4 | None = None
    description: str | None = Field(None, max_length=255)
    estimated_amount: Decimal | None = None
    actual_amount: Decimal | None = None


class ExpenseOut(Schema):
    uuid: UUID4
    wedding: UUID4 = Field(alias="wedding.uuid")
    category: UUID4 = Field(alias="category.uuid")
    contract: UUID4 | None = None
    description: str
    estimated_amount: Decimal
    actual_amount: Decimal

    @staticmethod
    def resolve_contract(obj: "Expense") -> UUID4 | None:
        return obj.contract.uuid if getattr(obj, "contract", None) else None


# --- INSTALLMENT SCHEMAS ---
class InstallmentIn(Schema):
    expense: UUID4
    installment_number: int
    amount: Decimal
    due_date: date
    paid_date: date | None = None
    notes: str | None = None


class InstallmentPatchIn(Schema):
    installment_number: int | None = None
    amount: Decimal | None = None
    due_date: date | None = None
    paid_date: date | None = None
    notes: str | None = None


class InstallmentOut(Schema):
    uuid: UUID4
    wedding: UUID4 = Field(alias="wedding.uuid")
    expense: UUID4 = Field(alias="expense.uuid")
    installment_number: int
    amount: Decimal
    due_date: date
    paid_date: date | None = None
    status: str
    notes: str | None = None
