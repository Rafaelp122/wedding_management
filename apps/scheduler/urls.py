from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth.decorators import login_required

from . import api_views, views

app_name = "scheduler"

# ===== API REST (FullCalendar) ===== #
router = DefaultRouter()
router.register(r"api/events", api_views.EventViewSet, basename="event")


urlpatterns = [
    # Endpoints da API
    path("", include(router.urls)),
    # Calendário parcial via HTMX
    path(
        "partial/<int:wedding_id>/",
        login_required(views.SchedulerPartialView.as_view()),
        name="partial_scheduler",
    ),
    # Criar evento
    path(
        "partial/<int:wedding_id>/event/new/",
        views.EventFormView.as_view(),
        name="event_new",
    ),
    # Editar evento
    path(
        "partial/<int:wedding_id>/event/<int:event_id>/edit/",
        views.EventFormView.as_view(),
        name="event_edit",
    ),
    # Criar evento (POST)
    path(
        "partial/<int:wedding_id>/event/save/",
        views.EventSaveView.as_view(),
        name="event_save",
    ),
    # Atualizar evento existente
    path(
        "partial/<int:wedding_id>/event/<int:event_id>/save/",
        views.EventSaveView.as_view(),
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
