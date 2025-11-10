from django.urls import path
from . import views

# Define o namespace para o app de contratos
app_name = "scheduler"

# Rotas principais do agendador de eventos
urlpatterns = [
    # Lista todos os eventos do planner
    path("list/", views.EventListView.as_view(), name="list"),

    # Cria um novo evento
    path("new/", views.EventCreateView.as_view(), name="new"),

    # Edita um evento existente
    path("edit/<int:event_id>/", views.EventUpdateView.as_view(), name="edit"),

    # Exclui um evento existente
    path("delete/<int:event_id>/", views.EventDeleteView.as_view(), name="delete"),

    # Exibe o calendário parcial vinculado a um casamento
    path(
        "partial/<int:wedding_id>/",
        views.PartialSchedulerView.as_view(),
        name="partial_scheduler",
    ),

    # API para buscar eventos em formato JSON
    path("api/events/<int:wedding_id>/", views.event_api, name="event_api"),

    # Gerencia criação, edição e exclusão via modal no calendário
    path(
        "manage/<int:wedding_id>/",
        views.ManageEventView.as_view(),
        name="manage_event",
    ),
]
