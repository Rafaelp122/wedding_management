"""
QuerySets customizados para o domínio de casamentos (Weddings).
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import TYPE_CHECKING

from django.db.models import Q

from apps.core.exceptions import BusinessRuleViolation
from apps.tenants.managers import TenantQuerySet


if TYPE_CHECKING:
    from apps.weddings.models import Wedding  # noqa: F401


class WeddingQuerySet(TenantQuerySet["Wedding"]):
    """QuerySet customizado para Wedding com métodos encadeáveis."""

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
