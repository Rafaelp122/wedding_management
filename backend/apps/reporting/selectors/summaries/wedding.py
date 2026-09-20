"""
Selectors para resumos e estatísticas consolidadas de casamentos.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Any

from django.db.models import Count, OuterRef, QuerySet, Subquery
from django.db.models.functions import Coalesce

from apps.finances.models import Budget, Installment
from apps.scheduler.models import Task
from apps.weddings.models import Wedding


if TYPE_CHECKING:
    from apps.tenants.models import Company


class WeddingSummarySelector:
    """
    Camada de consulta analítica para consolidação de resumos, métricas e
    estatísticas de casamentos.
    Centraliza subqueries cruzadas com outros domínios (finances, scheduler)
    para manter os models do domínio weddings puros.
    """

    @staticmethod
    def list_weddings_with_metrics(
        *,
        company: Company,
        search: str = "",
        status: str = "",
    ) -> QuerySet[Wedding]:
        """
        Retorna o QuerySet encadeável de casamentos do tenant com métricas embutidas
        (orçamento total, parcelas em atraso e tarefas pendentes).

        Args:
            company: O tenant atual para isolamento de dados.
            search: Termo de busca textual para filtrar por noivos ou local.
            status: Filtro opcional por status do casamento.

        Returns:
            QuerySet[Wedding] com anotações de total_budget, overdue_installments
            e incomplete_tasks.
        """
        qs = (
            Wedding.objects.for_tenant(company)
            .select_related("company")
            .search(search)
            .by_status(status)
        )

        return qs.annotate(
            total_budget=Subquery(
                Budget.objects.filter(
                    wedding=OuterRef("pk"), company=OuterRef("company")
                ).values("total_estimated")[:1]
            ),
            overdue_installments=Coalesce(
                Subquery(
                    Installment.objects.filter(
                        wedding=OuterRef("pk"),
                        company=OuterRef("company"),
                        status=Installment.StatusChoices.OVERDUE,
                    )
                    .values("wedding")
                    .annotate(cnt=Count("id"))
                    .values("cnt")[:1]
                ),
                0,
            ),
            incomplete_tasks=Coalesce(
                Subquery(
                    Task.objects.filter(
                        wedding=OuterRef("pk"),
                        company=OuterRef("company"),
                        is_completed=False,
                    )
                    .values("wedding")
                    .annotate(cnt=Count("id"))
                    .values("cnt")[:1]
                ),
                0,
            ),
        )

    @staticmethod
    def critical_weddings(
        *,
        company: Company,
        today: date,
        limit: int = 5,
    ) -> QuerySet[Wedding]:
        """
        Retorna os casamentos em andamento nos próximos 90 dias anotados com
        métricas críticas.

        Args:
            company: O tenant atual para isolamento de dados.
            today: Data de referência para prazos.
            limit: Quantidade máxima de registros (padrão: 5).

        Returns:
            QuerySet[Wedding] ordenado por data e anotado com métricas críticas.
        """
        qs = (
            Wedding.objects.for_tenant(company)
            .by_status(Wedding.StatusChoices.IN_PROGRESS)
            .upcoming(today=today, days=90)
        )

        return qs.annotate(
            incomplete_tasks=Coalesce(
                Subquery(
                    Task.objects.filter(
                        wedding=OuterRef("pk"),
                        company=OuterRef("company"),
                        is_completed=False,
                    )
                    .values("wedding")
                    .annotate(cnt=Count("id"))
                    .values("cnt")[:1]
                ),
                0,
            ),
            pending_installments=Coalesce(
                Subquery(
                    Installment.objects.filter(
                        wedding=OuterRef("pk"),
                        company=OuterRef("company"),
                        status=Installment.StatusChoices.PENDING,
                    )
                    .values("wedding")
                    .annotate(cnt=Count("id"))
                    .values("cnt")[:1]
                ),
                0,
            ),
            overdue_tasks=Coalesce(
                Subquery(
                    Task.objects.filter(
                        wedding=OuterRef("pk"),
                        company=OuterRef("company"),
                        is_completed=False,
                        due_date__lt=today,
                    )
                    .values("wedding")
                    .annotate(cnt=Count("id"))
                    .values("cnt")[:1]
                ),
                0,
            ),
            overdue_installments=Coalesce(
                Subquery(
                    Installment.objects.filter(
                        wedding=OuterRef("pk"),
                        company=OuterRef("company"),
                        status=Installment.StatusChoices.OVERDUE,
                    )
                    .values("wedding")
                    .annotate(cnt=Count("id"))
                    .values("cnt")[:1]
                ),
                0,
            ),
        ).order_by("date")[:limit]

    @staticmethod
    def upcoming_weddings_detail(
        *,
        company: Company,
        today: date | None = None,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Retorna os Top N casamentos futuros do tenant com contagem regressiva de dias.

        Args:
            company: O tenant atual para isolamento de dados.
            today: Data de referência (caso não informada, usa a data atual).
            limit: Quantidade máxima de casamentos retornados (padrão: 5).

        Returns:
            Lista de dicionários contendo uuid, bride_name, groom_name,
            date e days_until.
        """
        today = today or date.today()
        weddings = (
            Wedding.objects.for_tenant(company)
            .exclude(status=Wedding.StatusChoices.CANCELED)
            .filter(date__gte=today)
            .order_by("date")[:limit]
        )
        return [
            {
                "uuid": w.uuid,
                "bride_name": w.bride_name,
                "groom_name": w.groom_name,
                "date": w.date,
                "days_until": w.get_days_until(today),
            }
            for w in weddings
        ]


upcoming_weddings_detail = WeddingSummarySelector.upcoming_weddings_detail
