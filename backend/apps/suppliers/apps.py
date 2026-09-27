"""Configuração do aplicativo de Fornecedores."""

from django.apps import AppConfig


class SuppliersConfig(AppConfig):
    """Configuração da app de gestão de fornecedores."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.suppliers"
    verbose_name = "Fornecedores"
