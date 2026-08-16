from __future__ import annotations

from typing import Any
from uuid import UUID

from apps.tenants.models import Company
from apps.weddings.selectors.dashboard_selectors import (
    dashboard_summary_selector,
    wedding_overview_selector,
)


class DashboardService:
    """
    Camada de serviço para consolidação de métricas do painel do usuário (Dashboard).

    Delega consultas agregadas para os selectors correspondentes.
    """

    @staticmethod
    def get_summary(company: Company) -> dict[str, Any]:
        """
        Gera um resumo consolidado de indicadores importantes para a empresa.

        Args:
            company: O tenant atual para isolamento de dados.

        Returns:
            Dicionário com KPIs consolidados e casamentos críticos.
        """
        return dashboard_summary_selector(company=company)

    @staticmethod
    def get_wedding_overview(
        company: Company, wedding_uuid: UUID | str
    ) -> dict[str, Any]:
        """
        Computa uma visão geral detalhada de um casamento específico.

        Args:
            company: O tenant atual para isolamento de dados.
            wedding_uuid: O identificador único (UUID) do casamento.

        Returns:
            Dicionário com os indicadores detalhados do casamento solicitado.
        """
        return wedding_overview_selector(company=company, wedding_uuid=wedding_uuid)
