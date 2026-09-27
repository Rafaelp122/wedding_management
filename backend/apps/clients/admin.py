"""
Configuração do Django Admin para o modelo Client.
"""

from django.contrib import admin

from apps.clients.models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Administração do modelo Client no painel Django."""

    list_display = ("name", "cpf", "email", "phone", "company", "created_at")
    search_fields = ("name", "cpf", "email", "phone")
    list_filter = ("company", "created_at")
    readonly_fields = ("uuid", "created_at", "updated_at")
