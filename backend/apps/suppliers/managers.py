"""QuerySets e Managers customizados para o domínio de fornecedores."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import Count, Q

from apps.tenants.managers import TenantManager, TenantQuerySet


if TYPE_CHECKING:
    from apps.tenants.models import Company


class SupplierQuerySet(TenantQuerySet["Supplier"]):
    """QuerySet customizado para Fornecedores."""

    def with_contracts_count(self) -> SupplierQuerySet:
        """Anota cada fornecedor com a contagem total de contratos vinculados.

        Returns:
            SupplierQuerySet com a anotação contracts_count.
        """
        return self.annotate(contracts_count=Count("contracts"))

    def search(self, query: str | None = None) -> SupplierQuerySet:
        """Filtra fornecedores por termo de busca em nome, e-mail, telefone ou CNPJ.

        Args:
            query: Termo de busca textual.

        Returns:
            SupplierQuerySet filtrado pelo termo informado.
        """
        if not query:
            return self
        term = query.strip()
        return self.filter(
            Q(name__icontains=term)
            | Q(email__icontains=term)
            | Q(phone__icontains=term)
            | Q(cnpj__icontains=term)
        )

    def active(self) -> SupplierQuerySet:
        """Filtra fornecedores disponíveis para novos contratos.

        Returns:
            SupplierQuerySet com fornecedores ativos.
        """
        return self.filter(is_active=True)


class SupplierManager(TenantManager["Supplier"]):
    """Manager com suporte a isolamento de tenant e métodos utilitários de fornecedor."""

    def get_queryset(self) -> SupplierQuerySet:
        return SupplierQuerySet(self.model, using=self._db)

    def for_tenant(self, company: Company) -> SupplierQuerySet:
        return self.get_queryset().for_tenant(company)

    def search(self, query: str) -> SupplierQuerySet:
        return self.get_queryset().search(query)

    def with_contracts_count(self) -> SupplierQuerySet:
        return self.get_queryset().with_contracts_count()

    def active(self) -> SupplierQuerySet:
        return self.get_queryset().active()
