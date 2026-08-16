"""
QuerySets customizados para o domínio de casamentos (Weddings).
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import TYPE_CHECKING

from django.db.models import Count, OuterRef, Q, Subquery
from django.db.models.functions import Coalesce

from apps.core.exceptions import BusinessRuleViolation
from apps.tenants.managers import TenantQuerySet


if TYPE_CHECKING:
    from apps.weddings.models import Wedding  # noqa: F401


class WeddingQuerySet(TenantQuerySet["Wedding"]):
    """QuerySet customizado para Wedding com métodos encadeáveis."""

    def with_metrics(self) -> WeddingQuerySet:
        """
        Anota total estimado, parcelas em atraso e tarefas incompletas via Subqueries.

        Returns:
            WeddingQuerySet com anotações de total_budget, overdue_installments
            e incomplete_tasks.
        """
        from apps.finances.models import Budget, Installment
        from apps.scheduler.models import Task

        return self.annotate(
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

    def with_critical_metrics(self, today: date) -> WeddingQuerySet:
        """
        Anota métricas críticas para o dashboard consolidado.

        Args:
            today: Data de referência para cálculo de tarefas e parcelas atrasadas.

        Returns:
            WeddingQuerySet com anotações de incomplete_tasks, pending_installments,
            overdue_tasks e overdue_installments.
        """
        from apps.finances.models import Installment
        from apps.scheduler.models import Task

        return self.annotate(
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
        )

    def search(self, query: str = "") -> WeddingQuerySet:
        """
        Filtra casamentos por termo de busca em groom_name, bride_name ou location.

        Args:
            query: Termo de busca textual.

        Returns:
            WeddingQuerySet filtrado pelo termo informado.
        """
        if not query:
            return self
        return self.filter(
            Q(groom_name__icontains=query)
            | Q(bride_name__icontains=query)
            | Q(location__icontains=query)
        )

    def by_status(self, status: str = "") -> WeddingQuerySet:
        """
        Filtra casamentos pelo status informado.

        Args:
            status: Status do casamento (ex: IN_PROGRESS, COMPLETED, CANCELED).

        Returns:
            WeddingQuerySet filtrado pelo status.

        Raises:
            BusinessRuleViolation: Se o status fornecido for inválido.
        """
        if not status:
            return self
        from apps.weddings.models import Wedding

        if status not in Wedding.StatusChoices.values:
            raise BusinessRuleViolation(
                detail=f"Status inválido: '{status}'.",
                code="wedding_invalid_status_filter",
            )
        return self.filter(status=status)

    def upcoming(self, today: date, days: int = 90) -> WeddingQuerySet:
        """
        Filtra casamentos que ocorrerão nos próximos `days` dias a partir de today.

        Args:
            today: Data de referência inicial.
            days: Quantidade de dias futuros para filtragem (padrão: 90).

        Returns:
            WeddingQuerySet filtrado pelo intervalo de datas.
        """
        return self.filter(date__lte=today + timedelta(days=days))

    def only_lookup(self) -> WeddingQuerySet:
        """
        Restringe os campos selecionados para uuid, bride_name e groom_name,
        ordenando pelo nome da noiva.

        Returns:
            WeddingQuerySet otimizado para componentes de seleção/lookup.
        """
        return self.only("uuid", "bride_name", "groom_name").order_by("bride_name")
