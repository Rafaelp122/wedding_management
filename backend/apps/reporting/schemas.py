"""
Schemas Pydantic / Django Ninja para o módulo de relatórios e dashboard.
"""

from __future__ import annotations

from ninja import Schema
from pydantic import UUID4

from apps.weddings.schemas import (
    WeddingDashboardCategoryOut,
    WeddingDashboardInstallmentOut,
    WeddingDashboardOut,
    WeddingDashboardTaskOut,
)


__all__ = [
    "CriticalWeddingOut",
    "DashboardSummaryOut",
    "WeddingDashboardCategoryOut",
    "WeddingDashboardInstallmentOut",
    "WeddingDashboardOut",
    "WeddingDashboardTaskOut",
]


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
