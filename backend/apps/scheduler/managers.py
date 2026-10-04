"""
QuerySets e Managers customizados para o domínio de agendamento (Scheduler).
"""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from django.db import models

from apps.tenants.managers import TenantQuerySet


if TYPE_CHECKING:
    from apps.scheduler.models import Event, Task  # noqa: F401
    from apps.weddings.models import Wedding


class TaskQuerySet(TenantQuerySet["Task"]):
    """QuerySet customizado para Task com métodos encadeáveis."""

    def for_wedding(
        self, wedding_id_or_instance: Wedding | UUID | str | int
    ) -> TaskQuerySet:
        """
        Filtra tarefas pertencentes a um casamento específico.

        Returns:
            QuerySet filtrado pelo casamento.
        """
        if hasattr(wedding_id_or_instance, "_meta"):
            return self.filter(wedding=wedding_id_or_instance)  # type: ignore[misc]
        if isinstance(wedding_id_or_instance, int):
            return self.filter(wedding_id=wedding_id_or_instance)
        return self.filter(wedding__uuid=wedding_id_or_instance)

    def completed(self) -> TaskQuerySet:
        """
        Filtra apenas tarefas concluídas.

        Returns:
            QuerySet com tarefas marcadas como concluídas.
        """
        return self.filter(is_completed=True)

    def pending(self) -> TaskQuerySet:
        """
        Filtra apenas tarefas pendentes (não concluídas).

        Returns:
            QuerySet com tarefas pendentes.
        """
        return self.filter(is_completed=False)

    def urgent(self, today: date) -> TaskQuerySet:
        """
        Filtra tarefas pendentes e atrasadas/vencendo até a data de referência.

        Args:
            today: Data base de referência para avaliar vencimento.

        Returns:
            QuerySet com tarefas urgentes.
        """
        return self.pending().filter(due_date__lte=today)

    def due_in_range(
        self, start_date: date | None = None, end_date: date | None = None
    ) -> TaskQuerySet:
        """
        Filtra tarefas com prazo de vencimento dentro de um intervalo de datas.

        Args:
            start_date: Limite inicial opcional do intervalo (inclusive).
            end_date: Limite final opcional do intervalo (inclusive).

        Returns:
            QuerySet filtrado pelo intervalo de vencimento.
        """
        qs = self
        if start_date is not None:
            qs = qs.filter(due_date__gte=start_date)
        if end_date is not None:
            qs = qs.filter(due_date__lte=end_date)
        return qs


# Alias canônico para alinhamento com a RFC-001 (ADR-031)
ChecklistItemQuerySet = TaskQuerySet


class EventQuerySet(TenantQuerySet["Event"]):
    """QuerySet customizado para Event com métodos encadeáveis."""

    def for_wedding(
        self, wedding_id_or_instance: Wedding | UUID | str | int
    ) -> EventQuerySet:
        """
        Filtra eventos pertencentes a um casamento específico.

        Returns:
            QuerySet filtrado pelo casamento.
        """
        if hasattr(wedding_id_or_instance, "_meta"):
            return self.filter(wedding=wedding_id_or_instance)  # type: ignore[misc]
        if isinstance(wedding_id_or_instance, int):
            return self.filter(wedding_id=wedding_id_or_instance)
        return self.filter(wedding__uuid=wedding_id_or_instance)

    def chronological(self) -> EventQuerySet:
        """
        Ordena os eventos cronologicamente por horário de início.

        Returns:
            QuerySet ordenado por start_time ascendente.
        """
        return self.order_by("start_time")

    def in_period(
        self,
        start_datetime: datetime | date | None = None,
        end_datetime: datetime | date | None = None,
    ) -> EventQuerySet:
        """
        Filtra eventos dentro de um período específico.

        Args:
            start_datetime: Limite inicial opcional do período (inclusive).
            end_datetime: Limite final opcional do período (inclusive).

        Returns:
            QuerySet filtrado pelo período informado.
        """
        qs = self
        if start_datetime is not None:
            if isinstance(start_datetime, datetime):
                qs = qs.filter(start_time__gte=start_datetime)
            else:
                qs = qs.filter(start_time__date__gte=start_datetime)
        if end_datetime is not None:
            if isinstance(end_datetime, datetime):
                qs = qs.filter(start_time__lte=end_datetime)
            else:
                qs = qs.filter(start_time__date__lte=end_datetime)
        return qs

    def by_type(self, event_type: str | models.TextChoices) -> EventQuerySet:
        """
        Filtra eventos pelo tipo especificado.

        Args:
            event_type: Tipo do evento pretendido (ex: reuniao, pagamento).

        Returns:
            QuerySet filtrado pelo tipo informado.
        """
        return self.filter(event_type=event_type)
