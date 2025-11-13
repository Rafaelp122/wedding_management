from django.contrib import admin
from .models import Event


# Configuração do modelo Event no painel administrativo do Django
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Define como o modelo Event será exibido e filtrado no admin."""

    # Campos exibidos na listagem
    list_display = (
        "id", "title", "start_time", "event_type", "wedding", "planner"
    )

    # Campos pesquisáveis
    search_fields = ("title", "description", "location")

    # Filtros laterais
    list_filter = ("event_type", "wedding", "planner", "start_time")

    # Exibe hierarquia de datas no topo da página
    date_hierarchy = "start_time"
