"""
QuerySets customizados para o domínio de contratos e termos aditivos.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from django.db.models import Count, F, OuterRef, Q, Subquery, Sum, Value
from django.db.models.functions import Coalesce

from apps.tenants.managers import TenantQuerySet


if TYPE_CHECKING:
    from apps.contracts.models.contract import Contract
    from apps.contracts.models.contract_addendum import (  # noqa: F401
        ContractAddendum,
    )
    from apps.weddings.models import Wedding


class ContractAddendumQuerySet(TenantQuerySet["ContractAddendum"]):
    """QuerySet customizado para Termos Aditivos de Contrato."""

    def for_contract(
        self, contract: UUID | str | Contract | None = None
    ) -> ContractAddendumQuerySet:
        """Filtra aditivos vinculados a um contrato específico.

        Args:
            contract: Instância, UUID ou identificador do contrato principal.

        Returns:
            QuerySet filtrado pelo contrato.
        """
        if not contract:
            return self
        if hasattr(contract, "uuid"):
            return self.filter(contract__uuid=contract.uuid)
        return self.filter(contract__uuid=contract)

    def by_status(self, status: str | None = None) -> ContractAddendumQuerySet:
        """Filtra aditivos pelo status informado.

        Args:
            status: Status do aditivo desejado (ex: PENDING, SIGNED, CANCELED).

        Returns:
            QuerySet filtrado pelo status.
        """
        if not status:
            return self
        return self.filter(status=status)

    def signed(self) -> ContractAddendumQuerySet:
        """Filtra aditivos formalmente assinados.

        Returns:
            QuerySet contendo apenas aditivos assinados.
        """
        return self.filter(status="SIGNED")


class ContractQuerySet(TenantQuerySet["Contract"]):
    """QuerySet customizado para Contratos."""

    def with_totals(self) -> ContractQuerySet:
        """Anota o contrato com informações e totais agregados de aditivos.

        Evita queries N+1 calculando montantes consolidados via Subquery.

        Returns:
            ContractQuerySet com todas as anotações agregadas.
        """
        from apps.contracts.models.contract_addendum import ContractAddendum

        addendums_signed_subquery = Subquery(
            ContractAddendum.objects.filter(
                company=OuterRef("company"),
                contract=OuterRef("pk"),
                status=ContractAddendum.StatusChoices.SIGNED,
            )
            .values("contract")
            .annotate(s=Sum("amount"))
            .values("s")[:1]
        )

        addendums_active_subquery = Subquery(
            ContractAddendum.objects.filter(
                company=OuterRef("company"),
                contract=OuterRef("pk"),
            )
            .exclude(status=ContractAddendum.StatusChoices.CANCELED)
            .values("contract")
            .annotate(cnt=Count("id"))
            .values("cnt")[:1]
        )

        addendums_pending_subquery = Subquery(
            ContractAddendum.objects.filter(
                company=OuterRef("company"),
                contract=OuterRef("pk"),
                status=ContractAddendum.StatusChoices.PENDING,
            )
            .values("contract")
            .annotate(s=Sum("amount"))
            .values("s")[:1]
        )

        return self.select_related("supplier", "wedding", "expense", "client").annotate(  # type: ignore[no-redef]
            supplier_name=F("supplier__name"),
            supplier_phone=F("supplier__phone"),
            supplier_email=F("supplier__email"),
            client_name=F("client__name"),
            base_amount=F("total_amount"),
            addendums_count=Coalesce(addendums_active_subquery, 0),
            addendums_total=Coalesce(addendums_signed_subquery, Value(Decimal("0.00"))),
            addendums_pending_total=Coalesce(
                addendums_pending_subquery, Value(Decimal("0.00"))
            ),
            effective_amount=F("total_amount")
            + Coalesce(addendums_signed_subquery, Value(Decimal("0.00"))),
        )

    def by_status(self, status: str | None = None) -> ContractQuerySet:
        """Filtra contratos pelo status especificado.

        Args:
            status: Status desejado (ex: DRAFT, PENDING, SIGNED, CANCELED).

        Returns:
            ContractQuerySet filtrado pelo status.
        """
        if not status:
            return self
        return self.filter(status=status)

    def by_type(self, contract_type: str | None = None) -> ContractQuerySet:
        """Filtra contratos pelo tipo de contrato especificado.

        Args:
            contract_type: Tipo do contrato (ex: PLANNER, SUPPLIER).

        Returns:
            ContractQuerySet filtrado pelo tipo.
        """
        if not contract_type:
            return self
        return self.filter(contract_type=contract_type)

    def for_wedding(
        self, wedding: UUID | str | Wedding | None = None
    ) -> ContractQuerySet:
        """Filtra contratos associados a um casamento específico.

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

    def search(self, query: str | None = None) -> ContractQuerySet:
        """Filtra contratos por termo de busca textual.

        Args:
            query: Termo de busca textual.

        Returns:
            ContractQuerySet filtrado.
        """
        if not query:
            return self
        return self.filter(
            Q(name__icontains=query)
            | Q(supplier__name__icontains=query)
            | Q(client__name__icontains=query)
            | Q(description__icontains=query)
        )
