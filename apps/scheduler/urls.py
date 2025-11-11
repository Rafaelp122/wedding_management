from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from apps.weddings.models import Wedding
from . import api_views
from . import views_htmx

app_name = "scheduler"

# 🔹 API REST (usada pelo FullCalendar para carregar eventos)

router = DefaultRouter()
router.register(r"api/events", api_views.EventViewSet, basename="event")

# 🔹 View parcial (carrega o calendário dentro do detalhe do casamento)

class SchedulerPartialView(TemplateView):
    """Renderiza o calendário HTMX dentro do detalhe do casamento."""
    template_name = "scheduler/partials/_scheduler_partial.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wedding_id = kwargs.get("wedding_id")
        context["wedding"] = get_object_or_404(Wedding, id=wedding_id)
        return context

urlpatterns = [
    # API REST
    path("", include(router.urls)),

    # Parcial HTMX para o calendário
    path(
        "partial/<int:wedding_id>/",
        login_required(SchedulerPartialView.as_view()),
        name="partial_scheduler",
    ),

    # CRUD HTMX (criar / editar / salvar / deletar)
    path(
        "partial/<int:wedding_id>/event/new/",
        login_required(views_htmx.event_form),
        name="event_new",
    ),
    path(
        "partial/<int:wedding_id>/event/<int:event_id>/edit/",
        login_required(views_htmx.event_form),
        name="event_edit",
    ),
    path(
        "partial/<int:wedding_id>/event/save/",
        login_required(views_htmx.event_save),
        name="event_save",
    ),
    path(
        "partial/<int:wedding_id>/event/<int:event_id>/save/",
        login_required(views_htmx.event_save),
        name="event_update",
    ),
    path(
        "partial/<int:wedding_id>/event/<int:event_id>/delete/",
        login_required(views_htmx.event_delete),
        name="event_delete",
    ),
]
