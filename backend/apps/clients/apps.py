"""
Configuração da aplicação Django para o módulo de clientes e contatos.
"""

from django.apps import AppConfig


class ClientsConfig(AppConfig):
    """Configurações da aplicação de clientes e contatos."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.clients"
    verbose_name = "Clientes e Contatos"
