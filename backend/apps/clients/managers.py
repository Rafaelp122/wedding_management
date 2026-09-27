"""
Managers e QuerySets para o modelo Client do domínio de clientes.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Self

from django.db.models import Q

from apps.tenants.managers import TenantManager, TenantQuerySet


if TYPE_CHECKING:
    from apps.clients.models import Client  # noqa: F401
    from apps.tenants.models import Company


class ClientQuerySet(TenantQuerySet["Client"]):
    """QuerySet com métodos de busca e filtros para clientes do tenant."""

    def search(self, query: str) -> Self:
        """
        Filtra clientes com correspondência em nome, CPF, e-mail ou telefone.

        Args:
            query: Termo de busca textual.

        Returns:
            QuerySet filtrado pelo termo de busca.
        """
        term = query.strip()
        if not term:
            return self
        return self.filter(
            Q(name__icontains=term)
            | Q(cpf__icontains=term)
            | Q(email__icontains=term)
            | Q(phone__icontains=term)
        )


class ClientManager(TenantManager["Client"]):
    """Manager com suporte a isolamento de tenant e buscas textuais."""

    def get_queryset(self) -> ClientQuerySet:
        return ClientQuerySet(self.model, using=self._db)

    def for_tenant(self, company: Company) -> ClientQuerySet:
        return self.get_queryset().for_tenant(company)

    def search(self, query: str) -> ClientQuerySet:
        """Executa busca de clientes usando o QuerySet customizado."""
        return self.get_queryset().search(query)
