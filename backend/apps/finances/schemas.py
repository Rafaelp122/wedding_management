from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ninja import Schema
from pydantic import UUID4, Field


if TYPE_CHECKING:
    from apps.finances.models.budget import Budget
    from apps.finances.models.budget_category import BudgetCategory
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
    total_overall_spent: Decimal = Field(default=Decimal("0.00"))
    notes: str | None = None

    @staticmethod
    def resolve_total_overall_spent(obj: "Budget") -> Decimal:
        """Expõe o computed property ``Budget.total_overall_spent`` no payload JSON."""
        return obj.total_overall_spent


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
    total_spent: Decimal = Field(default=Decimal("0.00"))

    @staticmethod
    def resolve_total_spent(obj: "BudgetCategory") -> Decimal:
        """Expõe o computed property ``BudgetCategory.total_spent`` no payload JSON."""
        return obj.total_spent


# --- EXPENSE SCHEMAS ---
class ExpenseIn(Schema):
    category: UUID4
    contract: UUID4 | None = None
    name: str = Field(..., max_length=255)
    description: str | None = None
    estimated_amount: Decimal
    actual_amount: Decimal
    num_installments: int | None = Field(None, gt=0)
    first_due_date: date | None = None


class ExpensePatchIn(Schema):
    contract: UUID4 | None = None
    name: str | None = Field(None, max_length=255)
    description: str | None = None
    estimated_amount: Decimal | None = None
    actual_amount: Decimal | None = None
    num_installments: int | None = Field(None, gt=0)
    first_due_date: date | None = None


class ExpenseOut(Schema):
    uuid: UUID4
    wedding: UUID4 = Field(alias="wedding.uuid")
    category: UUID4 = Field(alias="category.uuid")
    contract: UUID4 | None = None
    name: str
    description: str = ""
    estimated_amount: Decimal
    actual_amount: Decimal
    category_name: str = ""
    contract_description: str | None = None
    status: str = "PENDING"
    installments_count: int = 0
    paid_installments_count: int = 0
    total_paid: Decimal = Decimal("0.00")
    total_pending: Decimal = Decimal("0.00")

    @staticmethod
    def resolve_contract(obj: "Expense") -> UUID4 | None:
        c = obj.contract
        return c.uuid if c else None

    @staticmethod
    def resolve_category_name(obj: "Expense") -> str:
        return getattr(obj, "category_name", obj.category.name)

    @staticmethod
    def resolve_contract_description(obj: "Expense") -> str | None:
        if obj.contract:
            return getattr(obj, "contract_description", obj.contract.description)
        return None

    @staticmethod
    def resolve_status(obj: "Expense") -> str:
        total = getattr(obj, "installments_count", obj.installments.count())
        paid = getattr(
            obj,
            "paid_installments_count",
            obj.installments.filter(status="PAID").count(),
        )
        if total == 0:
            return "PENDING"
        if paid >= total:
            return "SETTLED"
        if paid > 0:
            return "PARTIALLY_PAID"
        return "PENDING"

    @staticmethod
    def resolve_installments_count(obj: "Expense") -> int:
        return getattr(obj, "installments_count", obj.installments.count())

    @staticmethod
    def resolve_paid_installments_count(obj: "Expense") -> int:
        return getattr(
            obj,
            "paid_installments_count",
            obj.installments.filter(status="PAID").count(),
        )

    @staticmethod
    def resolve_total_paid(obj: "Expense") -> Decimal:
        from decimal import Decimal as D

        return getattr(obj, "total_paid", D("0.00"))

    @staticmethod
    def resolve_total_pending(obj: "Expense") -> Decimal:
        from decimal import Decimal as D

        return getattr(obj, "total_pending", D("0.00"))


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


class InstallmentAdjustIn(Schema):
    amount: Decimal | None = None
    due_date: date | None = None


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
