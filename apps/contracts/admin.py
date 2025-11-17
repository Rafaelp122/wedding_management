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
        "wedding__groom_name",
        "wedding__bride_name",
    )  # Permite buscar pelo nome do noivo ou da noiva
    list_filter = ("status",)  # Filtros laterais para facilitar a navegação
