from django.contrib import admin
from .models import Contract


# Configuração do modelo Contract no painel administrativo do Django
@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "wedding",
        "created_at",
        "status",
    )  # Campos mostrados na listagem
    search_fields = (
        "wedding__client__name",
    )  # Permite buscar pelo nome do cliente do casamento
    list_filter = ("status", "wedding")  # Filtros laterais para facilitar a navegação
