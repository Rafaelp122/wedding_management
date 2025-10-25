# -------------------------------------------------------------------
# MENSAGEM IMPORTANTE:
# Este ficheiro 'urls.py' foi totalmente corrigido.
# 1. Ele agora aponta para as views do CRUD de Evento
#    (EventListView, EventCreateView, etc.).
# 2. Ele também mantém as rotas da API que o seu 
#    calendário interativo precisa (partial_scheduler, manage_event).
# -------------------------------------------------------------------

from django.urls import path
from . import views

# app_name é VITAL para a tag {% url %} funcionar
app_name = 'scheduler' 

urlpatterns = [
    # -------------------------------------
    # Rotas do CRUD (Requisito 1)
    # -------------------------------------
    
    # scheduler/list/
    path('list/', views.EventListView.as_view(), name='list'),
    
    # scheduler/new/
    path('new/', views.EventCreateView.as_view(), name='new'),
    
    # scheduler/edit/1/
    path('edit/<int:event_id>/', views.EventUpdateView.as_view(), name='edit'),
    
    # scheduler/delete/1/
    path('delete/<int:event_id>/', views.EventDeleteView.as_view(), name='delete'),

    # -------------------------------------
    # Rotas da API do Calendário Interativo
    # -------------------------------------
    
    # Rota para carregar o calendário (HTMX)
    path(
        'partial/<int:wedding_id>/', 
        views.partial_scheduler, 
        name='partial_scheduler'
    ),
    
    # Rota para o JavaScript (FullCalendar) gerir os eventos
    path(
        'manage/<int:wedding_id>/',
        views.manage_event,
        name='manage_event'
    ),
]

