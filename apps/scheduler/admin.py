# Em apps/scheduler/admin.py

from django.contrib import admin
from .models import Schedule  # Verifique se o import está correto

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    """
    Admin para o modelo Schedule (Eventos da Agenda).
    """
    
    # Campos que REALMENTE existem no models.py:
    list_display = (
        'title', 
        'wedding', 
        'start_datetime', 
        'end_datetime'
    )
    
    # Filtros baseados em campos que existem:
    list_filter = (
        'wedding',         # Permite filtrar por casamento
        'start_datetime'   # Permite filtrar por data
    )
    
    # Facilita a busca no admin:
    search_fields = (
        'title', 
        'description', 
        'wedding__bride_name',  # Busca dentro do modelo relacionado
        'wedding__groom_name'
    )
    
    # Organiza o formulário de edição:
    fieldsets = (
        (None, {
            'fields': ('wedding', 'title', 'description')
        }),
        ('Datas do Evento', {
            'fields': ('start_datetime', 'end_datetime')
        }),
    )