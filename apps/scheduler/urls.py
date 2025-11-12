# scheduler/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from apps.weddings.models import Wedding
from . import api_views
from . import views 

app_name = "scheduler"

# Configuração da API REST utilizada pelo FullCalendar
# Responsável por fornecer os dados dos eventos via endpoints.
router = DefaultRouter()
router.register(r"api/events", api_views.EventViewSet, basename="event")


class SchedulerPartialView(TemplateView):
    """
    Renderiza o componente parcial do calendário (HTMX)
    vinculado a um casamento específico.
    """
    template_name = "scheduler/partials/_scheduler_partial.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wedding_id = kwargs.get("wedding_id")
        context["wedding"] = get_object_or_404(Wedding, id=wedding_id)
        return context


urlpatterns = [
    # Endpoints da API REST
    path("", include(router.urls)),

    # Renderização parcial do calendário, usada dentro do detalhe do casamento
    path(
        "partial/<int:wedding_id>/",
        login_required(SchedulerPartialView.as_view()),
        name="partial_scheduler",
    ),

    # Exibe o formulário para criação de um novo evento
    path(
        "partial/<int:wedding_id>/event/new/",
        views.EventFormView.as_view(),
        name="event_new",
    ),

    # Exibe o formulário para edição de um evento existente
    path(
        "partial/<int:wedding_id>/event/<int:event_id>/edit/",
        views.EventFormView.as_view(),
        name="event_edit",
    ),

    # Recebe o POST de um novo evento e realiza o salvamento
    path(
        "partial/<int:wedding_id>/event/save/",
        views.EventSaveView.as_view(),
        name="event_save",
    ),

    # Atualiza um evento existente com base no ID informado
    path(
        "partial/<int>wedding_id>/event/<int:event_id>/save/",
        views.EventSaveView.as_view(),
        name="event_update",
    ),

    # Exibe o modal de confirmação e realiza a exclusão do evento
    path(
        "partial/<int:wedding_id>/event/<int:event_id>/delete/",
        views.EventDeleteView.as_view(),
        name="event_delete",
    ),
]
