import datetime

from ninja import Field, Schema
from pydantic import UUID4


class WeddingIn(Schema):
    model_config = {"extra": "ignore"}

    groom_name: str
    bride_name: str
    date: datetime.date
    location: str
    expected_guests: int | None = None
    template: str | None = None


class WeddingPatchIn(Schema):
    model_config = {"extra": "ignore"}

    groom_name: str | None = None
    bride_name: str | None = None
    date: datetime.date | None = None
    location: str | None = None
    expected_guests: int | None = None
    status: str | None = None


class WeddingOut(Schema):
    uuid: UUID4
    groom_name: str
    bride_name: str
    date: datetime.date
    location: str
    expected_guests: int | None
    status: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    total_budget: float | None = Field(None, ge=0)
    overdue_installments: int = Field(0, ge=0)
    incomplete_tasks: int = Field(0, ge=0)


# ── Global Dashboard ──


class CriticalWeddingOut(Schema):
    uuid: UUID4
    groom_name: str
    bride_name: str
    days_until: int
    incomplete_tasks: int
    pending_installments: int
    overdue_tasks: int
    overdue_installments: int


class DashboardSummaryOut(Schema):
    pending_installments_7d: str
    urgent_tasks_count: int
    overdue_installments_amount: str
    overdue_installments_count: int
    pending_contracts_count: int
    critical_weddings: list[CriticalWeddingOut]


# ── Wedding Dashboard ──


class WeddingDashboardInstallmentOut(Schema):
    uuid: UUID4
    installment_number: int
    amount: str
    due_date: datetime.date
    status: str


class WeddingDashboardTaskOut(Schema):
    uuid: UUID4
    title: str
    due_date: datetime.date | None = None


class WeddingDashboardCategoryOut(Schema):
    name: str
    allocated: str
    spent: str
    percentage: float


class WeddingDashboardOut(Schema):
    days_until_wedding: int
    budget_percentage_used: float
    tasks_completed: int
    tasks_total: int
    contracts_signed: int
    contracts_total: int
    upcoming_installments: list[WeddingDashboardInstallmentOut]
    urgent_tasks: list[WeddingDashboardTaskOut]
    categories_summary: list[WeddingDashboardCategoryOut]
