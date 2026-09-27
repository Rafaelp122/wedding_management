"""Configuração do Django Admin para o módulo de Contratos."""

from django.contrib import admin

from apps.contracts.models import Contract, ContractAddendum


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Administração de contratos no Django Admin."""

    list_display = (
        "name",
        "contract_type",
        "service_tier",
        "company",
        "wedding",
        "supplier",
        "total_amount",
        "status",
        "signed_date",
    )
    list_filter = ("contract_type", "service_tier", "status", "company")
    search_fields = (
        "name",
        "supplier__name",
        "wedding__bride_name",
        "wedding__groom_name",
    )


@admin.register(ContractAddendum)
class ContractAddendumAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Administração de termos aditivos no Django Admin."""

    list_display = ("contract", "amount", "status", "signed_date", "company")
    list_filter = ("status", "company")
    search_fields = ("contract__name", "justification")
