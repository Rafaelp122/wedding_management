"""
Selectors para resumos e estatísticas de contratos.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from apps.logistics.models import Contract


if TYPE_CHECKING:
    from apps.tenants.models import Company
    from apps.weddings.models import Wedding


class ContractSummarySelector:
    """
    Camada de consulta para consolidação de resumos e estatísticas de contratos.
    """

    @staticmethod
    def pending_contracts_count(*, company: Company) -> int:
        """
        Retorna a quantidade de contratos em rascunho ou pendentes do tenant.

        Args:
            company: O tenant atual para isolamento de dados.

        Returns:
            Quantidade total de contratos nos status DRAFT ou PENDING.
        """
        return (
            Contract.objects.for_tenant(company)
            .filter(
                status__in=[
                    Contract.StatusChoices.DRAFT,
                    Contract.StatusChoices.PENDING,
                ]
            )
            .count()
        )

    @staticmethod
    def wedding_contract_stats(
        *, company: Company, wedding: Wedding
    ) -> tuple[int, int]:
        """
        Retorna as estatísticas de contratos assinados e totais de um casamento.

        Considera apenas contratos que não foram cancelados no cômputo total.

        Args:
            company: O tenant atual para isolamento de dados.
            wedding: Instância do casamento a ser consultado.

        Returns:
            Uma tupla contendo (contratos_assinados, total_contratos_ativos).
        """
        contracts = Contract.objects.for_tenant(company).filter(wedding=wedding)
        total = contracts.exclude(status=Contract.StatusChoices.CANCELED).count()
        signed = contracts.filter(status=Contract.StatusChoices.SIGNED).count()
        return signed, total
