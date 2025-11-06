from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """
    Configuração para mostrar o modelo Event no painel de Admin.
    """

    # Usamos os campos que existem no modelo Event
    list_display = ("id", "title", "start_time", "event_type", "wedding", "planner")
    search_fields = ("title", "description", "location")

    # Filtramos por campos que existem no Event
    list_filter = ("event_type", "wedding", "planner", "start_time")

    # Opcional: Para facilitar a visualização de datas
    date_hierarchy = "start_time"
