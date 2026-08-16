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

    @classmethod
    def as_manager(cls) -> "TenantManager[_ModelT]":
        """Retorna uma instância de TenantManager configurada com este QuerySet."""
        manager = TenantManager.from_queryset(cls)()
        manager._built_with_as_manager = True
        return manager


class TenantManager(models.Manager[_ModelT]):
    """Manager padrão para modelos vinculados a um Tenant."""

    _queryset_class = TenantQuerySet

    def get_queryset(self) -> TenantQuerySet[_ModelT]:
        return self._queryset_class(self.model, using=self._db)

    def for_tenant(self, company: "Company") -> TenantQuerySet[_ModelT]:
        return self.get_queryset().for_tenant(company)
