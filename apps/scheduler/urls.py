from django.contrib.auth.decorators import login_required
from django.urls import path

from . import api_views, views

app_name = "scheduler"


urlpatterns = [
    # API JSON para FullCalendar (sem DRF)
    path(
        "api/events/",
        login_required(api_views.EventsJsonView.as_view()),
        name="events_json",
    ),
    # Calendário parcial via HTMX
    path(
        "partial/<int:wedding_id>/",
        login_required(views.SchedulerPartialView.as_view()),
        name="partial_scheduler",
    ),
    # Criar evento (GET + POST) - EventCreateView agora é CBV
    path(
        "partial/<int:wedding_id>/event/new/",
        views.EventCreateView.as_view(),
        name="event_new",
    ),
    path(
        "partial/<int:wedding_id>/event/create/",
        views.EventCreateView.as_view(),
        name="event_create",
    ),
    # Detalhes do evento (GET)
    path(
        "partial/<int:wedding_id>/event/<int:event_id>/detail/",
        views.EventDetailView.as_view(),
        name="event_detail",
    ),
    # Editar evento (GET + POST) - EventUpdateView agora é CBV
    path(
        "partial/<int:wedding_id>/event/<int:event_id>/edit/",
        views.EventUpdateView.as_view(),
        name="event_edit",
    ),
    path(
        "partial/<int:wedding_id>/event/<int:event_id>/update/",
        views.EventUpdateView.as_view(),
        name="event_update",
    ),
    # Modal genérico de confirmação
    path(
        "partial/<int:wedding_id>/event/<int:event_id>/delete/modal/",
        views.EventDeleteModalView.as_view(),
        name="event_delete_modal",
    ),
    # Delete real (POST)
    path(
        "partial/<int:wedding_id>/event/<int:event_id>/delete/",
        views.EventDeleteView.as_view(),
        name="event_delete",
    ),
]
