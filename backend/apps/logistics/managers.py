"""
QuerySets customizados para o domínio logístico.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from apps.tenants.managers import TenantQuerySet


if TYPE_CHECKING:
    from apps.contracts.models.contract import Contract
    from apps.weddings.models import Wedding


__all__ = [
    "ItemQuerySet",
]


class ItemQuerySet(TenantQuerySet["Item"]):
    """QuerySet customizado para itens de logística."""

    def for_contract(
        self, contract: UUID | str | Contract | None = None
    ) -> ItemQuerySet:
        """
        Filtra itens associados a um contrato específico.

        Args:
            contract: Instância de Contract, UUID ou string identificadora.

        Returns:
            ItemQuerySet filtrado pelo contrato.
        """
        if not contract:
            return self
        if hasattr(contract, "uuid"):
            return self.filter(contract__uuid=contract.uuid)
        return self.filter(contract__uuid=contract)

    def for_wedding(self, wedding: UUID | str | Wedding | None = None) -> ItemQuerySet:
        """
        Filtra itens associados a um casamento específico.

        Args:
            wedding: Instância de Wedding, UUID ou string identificadora.

        Returns:
            ItemQuerySet filtrado pelo casamento.
        """
        if not wedding:
            return self
        if hasattr(wedding, "uuid"):
            return self.filter(wedding__uuid=wedding.uuid)
        return self.filter(wedding__uuid=wedding)

    def by_status(self, status: str | None = None) -> ItemQuerySet:
        """
        Filtra itens pelo status de aquisição.

        Args:
            status: Status de aquisição (ex: PENDING, IN_PROGRESS, DONE).

        Returns:
            ItemQuerySet filtrado pelo status.
        """
        if not status:
            return self
        return self.filter(acquisition_status=status)

    def search(self, query: str | None = None) -> ItemQuerySet:
        """
        Filtra itens por busca textual no nome.

        Args:
            query: Termo de busca.

        Returns:
            ItemQuerySet filtrado pelo termo.
        """
        if not query:
            return self
        return self.filter(name__icontains=query)

    def with_details(self) -> ItemQuerySet:
        """
        Carrega relacionamentos de wedding, contract e fornecedor para evitar N+1.

        Returns:
            ItemQuerySet com select_related aplicado.
        """
        return self.select_related("wedding", "contract", "contract__supplier")
