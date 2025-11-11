from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from apps.weddings.models import Wedding
from . import api_views

app_name = "scheduler"

router = DefaultRouter()
router.register(r"api/events", api_views.EventViewSet, basename="event")


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

    # Parcial HTMX (corrigida)
    path(
        "partial/<int:wedding_id>/",
        login_required(SchedulerPartialView.as_view()),
        name="partial_scheduler",
    ),
]
