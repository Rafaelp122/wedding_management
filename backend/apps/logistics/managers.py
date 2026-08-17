"""
QuerySets customizados para o domínio logístico.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from django.db.models import Count, F, OuterRef, Q, Subquery, Sum, Value
from django.db.models.functions import Coalesce

from apps.tenants.managers import TenantQuerySet


if TYPE_CHECKING:
    from apps.logistics.models.contract import Contract
    from apps.logistics.models.item import Item  # noqa: F401
    from apps.logistics.models.supplier import Supplier  # noqa: F401
    from apps.weddings.models import Wedding


class SupplierQuerySet(TenantQuerySet["Supplier"]):
    """QuerySet customizado para Fornecedores."""

    def with_contracts_count(self) -> SupplierQuerySet:
        """
        Anota cada fornecedor com a contagem total de contratos vinculados.

        Returns:
            SupplierQuerySet com a anotação contracts_count.
        """
        return self.annotate(contracts_count=Count("contracts"))

    def search(self, query: str | None = None) -> SupplierQuerySet:
        """
        Filtra fornecedores por termo de busca em nome, e-mail, telefone ou CNPJ.

        Args:
            query: Termo de busca textual.

        Returns:
            SupplierQuerySet filtrado pelo termo informado.
        """
        if not query:
            return self
        return self.filter(
            Q(name__icontains=query)
            | Q(email__icontains=query)
            | Q(phone__icontains=query)
            | Q(cnpj__icontains=query)
        )


class ContractQuerySet(TenantQuerySet["Contract"]):
    """QuerySet customizado para Contratos."""

    def with_totals(self) -> ContractQuerySet:
        """
        Anota o contrato com informações do fornecedor, despesa vinculada,
        total pago e contagem de aditivos, evitando queries N+1.

        Returns:
            ContractQuerySet com todas as anotações agregadas.
        """
        from apps.finances.models import Expense, Installment

        return self.select_related("supplier", "wedding", "parent").annotate(
            supplier_name=F("supplier__name"),
            supplier_phone=F("supplier__phone"),
            supplier_email=F("supplier__email"),
            expense_id=Subquery(
                Expense.objects.filter(
                    company=OuterRef("company"),
                    contract=OuterRef("pk"),
                ).values("uuid")[:1]
            ),
            total_paid=Coalesce(
                Subquery(
                    Installment.objects.filter(
                        company=OuterRef("company"),
                        expense__contract=OuterRef("pk"),
                        status=Installment.StatusChoices.PAID,
                    )
                    .values("expense__contract")
                    .annotate(s=Sum("amount"))
                    .values("s")[:1]
                ),
                Value(Decimal("0.00")),
            ),
            addendums_count=Coalesce(
                Subquery(
                    self.model.objects.filter(
                        company=OuterRef("company"),
                        parent=OuterRef("pk"),
                    )
                    .values("parent")
                    .annotate(cnt=Count("id"))
                    .values("cnt")[:1]
                ),
                0,
            ),
        )

    def by_status(self, status: str | None = None) -> ContractQuerySet:
        """
        Filtra contratos pelo status especificado.

        Args:
            status: Status desejado (ex: DRAFT, PENDING, SIGNED, CANCELED).

        Returns:
            ContractQuerySet filtrado pelo status.
        """
        if not status:
            return self
        return self.filter(status=status)

    def for_wedding(
        self, wedding: UUID | str | Wedding | None = None
    ) -> ContractQuerySet:
        """
        Filtra contratos associados a um casamento específico.

        Args:
            wedding: Instância de Wedding, UUID ou string identificadora.

        Returns:
            ContractQuerySet filtrado pelo casamento.
        """
        if not wedding:
            return self
        if hasattr(wedding, "uuid"):
            return self.filter(wedding__uuid=wedding.uuid)
        return self.filter(wedding__uuid=wedding)


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
