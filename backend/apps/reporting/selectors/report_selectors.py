"""
Selectors de agregação de dados para relatórios consolidados do casamento.
"""

import logging
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from apps.finances.models import BudgetCategory, Installment
from apps.logistics.models import Contract
from apps.reporting.selectors.dashboard_selectors import (
    wedding_overview_selector,
)
from apps.scheduler.models import Task
from apps.tenants.models import Company
from apps.weddings.models import Wedding
from apps.weddings.selectors import wedding_get_selector


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class WeddingReportDataDTO:
    """DTO imutável contendo os dados agregados para geração de relatórios."""

    wedding: Wedding
    overview: dict[str, Any]
    categories: list[BudgetCategory]
    installments: list[Installment]
    contracts: list[Contract]
    tasks: list[Task]


def wedding_report_data_selector(
    *,
    company: Company,
    wedding_uuid: UUID | str,
) -> WeddingReportDataDTO:
    """
    Agrega todos os conjuntos de dados necessários para a geração de relatórios.

    Args:
        company: Tenant autenticado.
        wedding_uuid: Identificador único do casamento.

    Returns:
        Instância tipada de WeddingReportDataDTO.
    """
    uuid_obj = (
        UUID(str(wedding_uuid)) if not isinstance(wedding_uuid, UUID) else wedding_uuid
    )
    wedding = wedding_get_selector(company=company, uuid=uuid_obj)
    overview = wedding_overview_selector(company=company, wedding_uuid=uuid_obj)

    logger.info(
        "Agregando dados de relatório para casamento uuid=%s, company_id=%s",
        wedding.uuid,
        company.id,
    )

    categories = list(
        BudgetCategory.objects.for_tenant(company)
        .filter(budget__wedding=wedding)
        .with_total_spent()
        .order_by("name")
    )
    installments = list(
        Installment.objects.for_tenant(company)
        .filter(wedding=wedding)
        .select_related("expense")
        .order_by("due_date")
    )
    contracts = list(
        Contract.objects.for_tenant(company)
        .filter(wedding=wedding)
        .select_related("supplier")
        .order_by("created_at")
    )
    tasks = list(
        Task.objects.for_tenant(company)
        .filter(wedding=wedding)
        .order_by("is_completed", "due_date")
    )

    return WeddingReportDataDTO(
        wedding=wedding,
        overview=overview,
        categories=categories,
        installments=installments,
        contracts=contracts,
        tasks=tasks,
    )
