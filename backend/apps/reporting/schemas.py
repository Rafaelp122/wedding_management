"""
Schemas Pydantic / Django Ninja para o módulo de relatórios e dashboard.
"""

from __future__ import annotations

import datetime

from ninja import Schema
from pydantic import UUID4


# ── Global Dashboard Schemas ──
class CriticalWeddingOut(Schema):
    """Métricas de atenção de um casamento crítico nos próximos 90 dias."""

    uuid: UUID4
    groom_name: str
    bride_name: str
    days_until: int
    incomplete_tasks: int
    pending_installments: int
    overdue_tasks: int
    overdue_installments: int


class DashboardSummaryOut(Schema):
    """Resumo consolidado de indicadores importantes para o dashboard da empresa."""

    pending_installments_7d: str
    urgent_tasks_count: int
    overdue_installments_amount: str
    overdue_installments_count: int
    pending_contracts_count: int
    critical_weddings: list[CriticalWeddingOut]


# ── Wedding Specific Dashboard / Overview Schemas ──
class WeddingDashboardInstallmentOut(Schema):
    """Métricas de parcela financeira no resumo do casamento."""

    uuid: UUID4
    installment_number: int
    amount: str
    due_date: datetime.date
    status: str


class WeddingDashboardTaskOut(Schema):
    """Métricas de tarefa no resumo do casamento."""

    uuid: UUID4
    title: str
    due_date: datetime.date | None = None


class WeddingDashboardCategoryOut(Schema):
    """Resumo de gastos por categoria no orçamento do casamento."""

    name: str
    allocated: str
    spent: str
    percentage: float


class WeddingDashboardOut(Schema):
    """Visão geral agregada de indicadores de um casamento específico."""

    days_until_wedding: int
    budget_percentage_used: float
    tasks_completed: int
    tasks_total: int
    contracts_signed: int
    contracts_total: int
    upcoming_installments: list[WeddingDashboardInstallmentOut]
    urgent_tasks: list[WeddingDashboardTaskOut]
    categories_summary: list[WeddingDashboardCategoryOut]
