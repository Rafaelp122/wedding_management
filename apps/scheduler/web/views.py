import logging

from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, TemplateView, UpdateView

from apps.core.mixins.auth import WeddingOwnershipMixin

from ..constants import (CONFIRM_DELETE_TEMPLATE, DELETE_OBJECT_TYPE,
                         EVENT_DETAIL_TEMPLATE, FORM_MODAL_CONTAINER_ID,
                         MODAL_CREATE_TITLE, MODAL_EDIT_TITLE,
                         SCHEDULER_PARTIAL_TEMPLATE, SUBMIT_CREATE_TEXT,
                         SUBMIT_EDIT_TEXT)
from .mixins import (EventFormLayoutMixin, EventFormMixin,
                     EventHtmxResponseMixin, EventModalContextMixin,
                     EventOwnershipMixin)

logger = logging.getLogger(__name__)


# CALENDÁRIO (PARCIAL VIA HTMX)
class SchedulerPartialView(WeddingOwnershipMixin, TemplateView):
    """
    Renderiza o calendário dentro do contexto de um casamento.
    """

    template_name = SCHEDULER_PARTIAL_TEMPLATE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["wedding"] = self.wedding
        logger.info(
            f"Scheduler calendar loaded for wedding_id={self.wedding.id}, "
            f"user={self.request.user.username}"
        )
        return context


# CRIAR EVENTO (GET + POST)
class EventCreateView(
    EventModalContextMixin,
    EventFormMixin,
    EventHtmxResponseMixin,
    EventFormLayoutMixin,
    WeddingOwnershipMixin,
    CreateView,
):
    """Cria um novo evento (GET exibe formulário, POST processa)."""

    modal_title = MODAL_CREATE_TITLE
    submit_button_text = SUBMIT_CREATE_TEXT

    def get_hx_post_url(self):
        """Retorna a URL para o POST do formulário."""
        return reverse("scheduler:event_create", args=[self.wedding.id])

    def get_form_kwargs(self):
        """Adiciona clicked_date ao form se veio do GET."""
        kwargs = super().get_form_kwargs()
        if self.request.method == "GET":
            clicked_date = self.request.GET.get("date")
            kwargs["clicked_date"] = clicked_date
        return kwargs

    def get_context_data(self, **kwargs):
        """Adiciona wedding ao contexto."""
        context = super().get_context_data(**kwargs)
        context["wedding"] = self.wedding

        if self.request.method == "GET":
            clicked_date = self.request.GET.get("date", "N/A")
            logger.info(
                f"Event creation form opened: wedding_id={self.wedding.id}, "
                f"user={self.request.user.username}, "
                f"clicked_date={clicked_date}"
            )

        return context


# DETALHES DO EVENTO
class EventDetailView(EventOwnershipMixin, WeddingOwnershipMixin, View):
    """Exibe os detalhes do evento no modal."""

    template_name = EVENT_DETAIL_TEMPLATE

    def get(self, request, *args, **kwargs):
        event_id = kwargs.get("event_id")
        event = self.get_event_or_404(event_id)

        logger.info(
            f"Event details viewed: event_id={event.id}, "
            f"title='{event.title}', "
            f"wedding_id={self.wedding.id}, "
            f"user={request.user.username}"
        )

        context = {
            "event": event,
            "wedding": self.wedding,
        }
        return render(request, self.template_name, context)


# FORMULÁRIO DE EVENTO - EDITAR
class EventUpdateFormView(
    EventModalContextMixin,
    EventOwnershipMixin,
    EventFormLayoutMixin,
    WeddingOwnershipMixin,
    View,
):
    """Renderiza o formulário preenchido para editar um evento existente."""

    modal_title = MODAL_EDIT_TITLE
    submit_button_text = SUBMIT_EDIT_TEXT

    def get_hx_post_url(self):
        """Retorna a URL para o POST do formulário."""
        return reverse(
            "scheduler:event_update", args=[self.wedding.id, self.event.id]
        )

    def get(self, request, *args, **kwargs):
        event_id = kwargs.get("event_id")
        self.event = self.get_event_or_404(event_id)

        form = self.form_class(instance=self.event)

        context = self.get_context_data(
            form=form, wedding=self.wedding, event=self.event
        )
        return render(request, self.template_name, context)


# EDITAR EVENTO (GET + POST)
class EventUpdateView(
    EventModalContextMixin,
    EventOwnershipMixin,
    EventFormMixin,
    EventHtmxResponseMixin,
    EventFormLayoutMixin,
    WeddingOwnershipMixin,
    UpdateView,
):
    """Edita um evento existente (GET exibe formulário, POST processa)."""

    modal_title = MODAL_EDIT_TITLE
    submit_button_text = SUBMIT_EDIT_TEXT

    def get_hx_post_url(self):
        """Retorna a URL para o POST do formulário."""
        return reverse(
            "scheduler:event_update", args=[self.wedding.id, self.object.id]
        )

    def get_object(self, queryset=None):
        """Obtém o evento a ser editado."""
        event_id = self.kwargs.get("event_id")
        self.event = self.get_event_or_404(event_id)
        return self.event

    def get_context_data(self, **kwargs):
        """Adiciona wedding e event ao contexto."""
        context = super().get_context_data(**kwargs)
        context["wedding"] = self.wedding
        context["event"] = self.object
        return context


# MODAL DE CONFIRMAÇÃO DE EXCLUSÃO (GENÉRICO)
class EventDeleteModalView(EventOwnershipMixin, WeddingOwnershipMixin, View):
    template_name = CONFIRM_DELETE_TEMPLATE

    def get(self, request, *args, **kwargs):
        event = self.get_event_or_404(kwargs["event_id"])

        context = {
            "hx_post_url": reverse(
                "scheduler:event_delete", args=[self.wedding.id, event.id]
            ),
            "hx_target_id": f"#{FORM_MODAL_CONTAINER_ID}",
            "object_type": DELETE_OBJECT_TYPE,
            "object_name": event.title,
        }
        return render(request, self.template_name, context)


# EXCLUSÃO DO EVENTO (POST)
class EventDeleteView(
    EventOwnershipMixin,
    EventHtmxResponseMixin,
    WeddingOwnershipMixin,
    View,
):
    """
    Deleta o evento e dispara trigger HTMX.
    """

    def post(self, request, *args, **kwargs):
        event = self.get_event_or_404(kwargs["event_id"])

        event_id = event.id
        event.delete()

        # Retorna resposta com trigger HTMX (via mixin)
        return self.render_event_deleted_response(event_id)
