from django.urls import path
# Importa TODAS as views necessárias
from . import views 

app_name = 'scheduler' 

urlpatterns = [
    # --- URLs do CRUD Tradicional ---
    path('list/', views.EventListView.as_view(), name='list'),
    path('new/', views.EventCreateView.as_view(), name='new'),
    # Usa <int:event_id> como no pk_url_kwarg das views
    path('edit/<int:event_id>/', views.EventUpdateView.as_view(), name='edit'), 
    path('delete/<int:event_id>/', views.EventDeleteView.as_view(), name='delete'),

    # --- URLs para o Calendário Interativo (FullCalendar) ---
    
    # URL para carregar o HTML parcial do calendário (chamada via HTMX)
    path(
        'partial/<int:wedding_id>/', 
        views.partial_scheduler, 
        name='partial_scheduler' 
    ),

    # ======================================================
    #   NOVA URL: API para buscar dados JSON dos eventos
    # ======================================================
    path(
        'api/events/<int:wedding_id>/', # wedding_id necessário para contexto (cores)
        views.event_api, 
        name='event_api' 
    ),
    # ======================================================
    
    # URL ÚNICA para gerir eventos via AJAX/HTMX (Criar/Editar/Mover/Apagar a partir do Modal/Calendário)
    path(
        'manage/<int:wedding_id>/', 
        views.manage_event, 
        name='manage_event' 
    ),
]

