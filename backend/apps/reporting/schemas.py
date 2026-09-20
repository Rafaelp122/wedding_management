"""
Schemas Pydantic / Django Ninja para o módulo de relatórios e dashboard.
"""

from __future__ import annotations

import datetime

from ninja import Schema
from pydantic import UUID4, Field


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


class DashboardInstallmentDetailOut(Schema):
    """Detalhes de parcela financeira para listas e modais no dashboard global."""

    uuid: UUID4
    wedding_name: str
    amount: str
    due_date: datetime.date
    installment_number: int
    status: str


class DashboardTaskDetailOut(Schema):
    """Detalhes de tarefa urgente para listas e modais no dashboard global."""

    uuid: UUID4
    wedding_name: str
    title: str
    due_date: datetime.date | None = None


class DashboardContractDetailOut(Schema):
    """Detalhes de contrato pendente para listas e modais no dashboard global."""

    uuid: UUID4
    wedding_name: str
    supplier_name: str
    total_amount: str
    status: str


class CashFlowMonthOut(Schema):
    """Projeção de fluxo de caixa mensal (parcelas pagas vs pendentes)."""

    month: int
    paid: str
    pending: str


class TaskProgressWeddingOut(Schema):
    """Progresso consolidado de tarefas agrupado por casamento."""

    wedding_uuid: UUID4
    wedding_name: str
    total_tasks: int
    completed_tasks: int
    progress_pct: int


class UpcomingWeddingOut(Schema):
    """Resumo simplificado de casamento próximo para o painel de operações."""

    uuid: UUID4
    bride_name: str
    groom_name: str
    date: datetime.date
    days_until: int


class DashboardOperationsOut(Schema):
    """Painel de operações consolidado (casamentos, tarefas e contratos)."""

    upcoming_weddings: list[UpcomingWeddingOut]
    urgent_tasks: list[DashboardTaskDetailOut]
    pending_contracts: list[DashboardContractDetailOut]


class DashboardSummaryOut(Schema):
    """Resumo consolidado de indicadores importantes para o dashboard da empresa."""

    pending_installments_7d: str
    urgent_tasks_count: int
    overdue_installments_amount: str
    overdue_installments_count: int
    pending_contracts_count: int
    critical_weddings: list[CriticalWeddingOut]
    upcoming_installments: list[DashboardInstallmentDetailOut] = Field(
        default_factory=list
    )
    overdue_installments: list[DashboardInstallmentDetailOut] = Field(
        default_factory=list
    )
    urgent_tasks: list[DashboardTaskDetailOut] = Field(default_factory=list)
    pending_contracts: list[DashboardContractDetailOut] = Field(default_factory=list)


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
    total_allocated: str = "0.00"
    total_spent: str = "0.00"
