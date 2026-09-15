"""
Selectors para resumos e estatísticas de contratos.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from apps.logistics.models import Contract


if TYPE_CHECKING:
    from django.db.models import QuerySet

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
        return int(
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
        total = int(contracts.exclude(status=Contract.StatusChoices.CANCELED).count())
        signed = int(contracts.filter(status=Contract.StatusChoices.SIGNED).count())
        return signed, total

    @staticmethod
    def annotate_financial_totals(
        qs: QuerySet[Contract],
    ) -> QuerySet[Contract]:
        """
        Anota contratos com informações financeiras agregadas (expense_id e total_paid)
        evitando queries N+1.
        """
        from decimal import Decimal

        from django.db.models import OuterRef, Subquery, Sum, Value
        from django.db.models.functions import Coalesce

        from apps.finances.models import Expense, Installment

        return qs.annotate(
            expense_id=Subquery(
                Expense.objects.filter(
                    company=OuterRef("company"),
                    contract=OuterRef("pk"),
                ).values("uuid")[:1]
            ),
            total_paid=Coalesce(
                Subquery(
                    Installment.objects.filter(
                        company=OuterRef("company"),
                        expense__contract=OuterRef("pk"),
                        status=Installment.StatusChoices.PAID,
                    )
                    .values("expense__contract")
                    .annotate(s=Sum("amount"))
                    .values("s")[:1]
                ),
                Value(Decimal("0.00")),
            ),
        )
