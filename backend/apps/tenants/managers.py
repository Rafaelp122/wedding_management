from __future__ import annotations

from typing import TYPE_CHECKING, Self, TypeVar

from django.db import models


if TYPE_CHECKING:
    from apps.tenants.models import Company

_ModelT = TypeVar("_ModelT", bound=models.Model)


class TenantQuerySet(models.QuerySet[_ModelT]):
    """QuerySet base para isolamento de dados por Tenant (Company)."""

    def for_tenant(self, company: Company) -> Self:
        """
        Filtra os registros pertencentes à empresa informada.

        Returns:
            QuerySet filtrado pelo tenant.
        """
        return self.filter(company=company)


class TenantManager(models.Manager[_ModelT]):
    """Manager padrão para modelos vinculados a um Tenant."""

    _queryset_class = TenantQuerySet

    def get_queryset(self) -> TenantQuerySet[_ModelT]:
        """
        Retorna o QuerySet customizado com suporte a isolamento de tenant.

        Returns:
            Instância de TenantQuerySet associada ao modelo.
        """
        return self._queryset_class(self.model, using=self._db)

    def for_tenant(self, company: Company) -> TenantQuerySet[_ModelT]:
        """
        Filtra os registros pertencentes à empresa informada.

        Returns:
            TenantQuerySet filtrado pelo tenant.
        """
        return self.get_queryset().for_tenant(company)
