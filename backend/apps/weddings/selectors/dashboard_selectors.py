"""
Selectors para o Dashboard consolidado e visão geral de casamento.
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Any
from uuid import UUID

from apps.tenants.models import Company
from apps.weddings.selectors.summaries import (
    ContractSummarySelector,
    FinancialSummarySelector,
    TaskSummarySelector,
)
from apps.weddings.selectors.wedding_selectors import (
    critical_weddings_selector,
    wedding_get_selector,
)


logger = logging.getLogger(__name__)


def dashboard_summary_selector(*, company: Company) -> dict[str, Any]:
    """
    Gera um resumo consolidado de indicadores importantes para o dashboard da empresa.

    Busca estatísticas financeiras gerais (parcelas a vencer e atrasadas),
    quantidade de tarefas urgentes, contratos pendentes e uma listagem
    de casamentos críticos ocorrendo nos próximos 90 dias com pendências.

    Args:
        company: O tenant atual para isolamento de dados.

    Returns:
        Dicionário contendo as chaves:
            - pending_installments_7d (str): Valor pendente em 7 dias formatado.
            - urgent_tasks_count (int): Tarefas urgentes acumuladas.
            - overdue_installments_amount (str): Valor total em atraso formatado.
            - overdue_installments_count (int): Quantidade de parcelas em atraso.
            - pending_contracts_count (int): Quantidade de contratos pendentes.
            - critical_weddings (list[dict]): Lista dos top 5 casamentos críticos.
    """
    logger.info(f"Computando resumo do dashboard para company_id={company.id}")
    today = date.today()

    pending_7d = FinancialSummarySelector.pending_installments_7d(
        company=company, today=today
    )
    overdue_amount, overdue_count = FinancialSummarySelector.overdue_installments(
        company=company, today=today
    )
    urgent_tasks_count = TaskSummarySelector.urgent_tasks_count(
        company=company, today=today
    )
    pending_contracts_count = ContractSummarySelector.pending_contracts_count(
        company=company
    )

    critical_qs = critical_weddings_selector(company=company, today=today, limit=5)

    critical_weddings = []
    for w in critical_qs:
        days_until = max(0, (w.date - today).days)
        critical_weddings.append(
            {
                "uuid": w.uuid,
                "groom_name": w.groom_name,
                "bride_name": w.bride_name,
                "days_until": days_until,
                "incomplete_tasks": w.incomplete_tasks,
                "pending_installments": w.pending_installments,
                "overdue_tasks": w.overdue_tasks,
                "overdue_installments": w.overdue_installments,
            }
        )

    logger.info(
        f"Dashboard resumo computado: company_id={company.id}, "
        f"critical_weddings={len(critical_weddings)}"
    )
    return {
        "pending_installments_7d": f"{pending_7d:.2f}",
        "urgent_tasks_count": urgent_tasks_count,
        "overdue_installments_amount": f"{overdue_amount:.2f}",
        "overdue_installments_count": overdue_count,
        "pending_contracts_count": pending_contracts_count,
        "critical_weddings": critical_weddings,
    }


def wedding_overview_selector(
    *,
    company: Company,
    wedding_uuid: UUID | str,
) -> dict[str, Any]:
    """
    Computa uma visão geral detalhada de indicadores de um casamento específico.

    Reúne métricas de contagem regressiva, uso do orçamento, progresso de tarefas,
    assinatura de contratos, parcelas financeiras a vencer, tarefas urgentes
    e resumo por categorias de despesa.

    Args:
        company: O tenant atual para isolamento de dados.
        wedding_uuid: O identificador único (UUID) do casamento.

    Returns:
        Dicionário com os indicadores consolidados do casamento.

    Raises:
        ObjectNotFoundError: Se o casamento não for encontrado ou acesso negado.
    """
    wedding = wedding_get_selector(company=company, uuid=wedding_uuid)
    logger.info(
        f"Computando visão geral do casamento uuid={wedding_uuid} "
        f"para company_id={company.id}"
    )
    today = date.today()
    days_until = max(0, (wedding.date - today).days)

    budget_pct = FinancialSummarySelector.budget_percentage_used(
        company=company, wedding=wedding
    )
    tasks_completed, tasks_total = TaskSummarySelector.wedding_task_stats(
        company=company, wedding=wedding
    )
    contracts_signed, contracts_total = ContractSummarySelector.wedding_contract_stats(
        company=company, wedding=wedding
    )
    upcoming_installments = FinancialSummarySelector.upcoming_installments(
        company=company, wedding=wedding, today=today
    )
    urgent_tasks = TaskSummarySelector.urgent_tasks(
        company=company, wedding=wedding, today=today
    )
    categories_summary = FinancialSummarySelector.categories_summary(
        company=company, wedding=wedding
    )

    logger.info(
        f"Visão geral do casamento uuid={wedding_uuid} computada: "
        f"days_until={days_until}, budget_pct={budget_pct}"
    )
    return {
        "days_until_wedding": days_until,
        "budget_percentage_used": budget_pct,
        "tasks_completed": tasks_completed,
        "tasks_total": tasks_total,
        "contracts_signed": contracts_signed,
        "contracts_total": contracts_total,
        "upcoming_installments": upcoming_installments,
        "urgent_tasks": urgent_tasks,
        "categories_summary": categories_summary,
    }
