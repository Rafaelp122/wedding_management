from django.contrib import admin
from .models import Item


# Configuração do modelo Item no painel administrativo do Django
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "quantity",
        "unit_price",
        "supplier",
        "wedding",
    )  # Campos exibidos na listagem
    search_fields = ("name",)  # Permite buscar itens pelo nome
    list_filter = ("supplier", "wedding")  # Filtros laterais por fornecedor e casamento
