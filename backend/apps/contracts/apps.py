"""Configuração do aplicativo Django de Contratos e Termos Aditivos."""

from django.apps import AppConfig


class ContractsConfig(AppConfig):
    """Configuração da aplicação de Contratos e Termos Aditivos (ADR-031)."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.contracts"
    verbose_name = "Contratos e Termos Aditivos"
