from typing import TYPE_CHECKING, TypeVar

from django.db import models


if TYPE_CHECKING:
    from apps.tenants.models import Company

_ModelT = TypeVar("_ModelT", bound=models.Model)


class TenantQuerySet(models.QuerySet[_ModelT]):
    """QuerySet base para isolamento de dados por Tenant (Company)."""

    def for_tenant(self, company: "Company") -> "TenantQuerySet[_ModelT]":
        """Filtra os registros estritamente pela empresa fornecida."""
        return self.filter(company=company)


class TenantManager(models.Manager[_ModelT]):
    """Manager padrão para modelos vinculados a um Tenant."""

    def get_queryset(self) -> TenantQuerySet[_ModelT]:
        return TenantQuerySet(self.model, using=self._db)

    def for_tenant(self, company: "Company") -> TenantQuerySet[_ModelT]:
        return self.get_queryset().for_tenant(company)
