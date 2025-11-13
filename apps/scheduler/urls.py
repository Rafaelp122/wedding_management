# apps/scheduler/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from apps.weddings.models import Wedding
from . import api_views, views

app_name = "scheduler"

# ===== API REST (FullCalendar) =====
# Endpoint usado pelo FullCalendar para carregar eventos dinamicamente.
router = DefaultRouter()
router.register(r"api/events", api_views.EventViewSet, basename="event")


# ===== View parcial (HTMX) =====
# Renderiza o calendário dentro do contexto de um casamento específico.
class SchedulerPartialView(TemplateView):
    template_name = "scheduler/partials/_scheduler_partial.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wedding_id = kwargs.get("wedding_id")
        context["wedding"] = get_object_or_404(Wedding, id=wedding_id)
        return context


# ===== URL Patterns =====
urlpatterns = [
    # Endpoints da API
    path("", include(router.urls)),

    # Renderização parcial do calendário (HTMX)
    path(
        "partial/<int:wedding_id>/",
        login_required(SchedulerPartialView.as_view()),
        name="partial_scheduler",
    ),

    # Exibição do formulário de criação de evento
    path(
        "partial/<int:wedding_id>/event/new/",
        views.EventFormView.as_view(),
        name="event_new",
    ),

    # Exibição do formulário de edição de evento
    path(
        "partial/<int:wedding_id>/event/<int:event_id>/edit/",
        views.EventFormView.as_view(),
        name="event_edit",
    ),

    # Salvamento de novo evento
    path(
        "partial/<int:wedding_id>/event/save/",
        views.EventSaveView.as_view(),
        name="event_save",
    ),

    # Atualização de evento existente
    path(
        "partial/<int:wedding_id>/event/<int:event_id>/save/",
        views.EventSaveView.as_view(),
        name="event_update",
    ),

    # Exclusão de evento com confirmação
    path(
        "partial/<int:wedding_id>/event/<int:event_id>/delete/",
        views.EventDeleteView.as_view(),
        name="event_delete",
    ),
]
