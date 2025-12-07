"""
Mixins específicos do app scheduler.

Este módulo contém mixins reutilizáveis para views do scheduler,
seguindo o princípio DRY (Don't Repeat Yourself).
"""

import json
import logging
from typing import ClassVar

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404

from apps.core.mixins.forms import FormLayoutMixin
from apps.core.mixins.views import ModalContextMixin

from ..constants import EVENT_FORM_MODAL_TEMPLATE, EVENT_SAVED_TRIGGER
from ..models import Event
from .forms import EventForm

logger = logging.getLogger(__name__)


class EventOwnershipMixin:
    """
    Mixin que facilita obtenção de eventos com verificação de ownership.

    Fornece método helper para buscar eventos garantindo que pertencem
    ao planner logado e ao wedding do contexto atual.

    Attributes:
        request: HttpRequest (fornecido pela View)
        wedding: Wedding instance (fornecido pelo WeddingOwnershipMixin)
    """

    def get_event_or_404(self, event_id):
        """
        Obtém evento garantindo ownership (planner + wedding).

        Args:
            event_id: ID do evento a ser buscado.

        Returns:
            Instância do Event validada.

        Raises:
            Http404: Se evento não existir ou não pertencer ao
                    usuário/wedding.
        """
        event = get_object_or_404(
            Event,
            id=event_id,
            planner=self.request.user,
            wedding=self.wedding,
        )

        logger.debug(
            f"Event retrieved: event_id={event.id}, "
            f"title='{event.title}', "
            f"wedding_id={self.wedding.id}, "
            f"user={self.request.user.username}"
        )

        return event


class EventHtmxResponseMixin:
    """
    Mixin para respostas HTMX padronizadas de eventos.

    Fornece métodos helpers para criar respostas HTTP com triggers
    HTMX específicos do domínio de eventos.
    """

    def render_event_saved_response(self):
        """
        Retorna resposta HTTP 204 com trigger eventSaved.

        Usado após criar ou atualizar evento com sucesso.
        O JavaScript do calendar.js escuta este trigger e
        atualiza o calendário.

        Returns:
            HttpResponse com status 204 e header HX-Trigger.
        """
        logger.info(f"Event saved successfully: " f"user={self.request.user.username}")

        response = HttpResponse(status=204)
        response["HX-Trigger"] = EVENT_SAVED_TRIGGER
        return response

    def render_event_deleted_response(self, event_id):
        """
        Retorna resposta JSON com trigger eventDeleted.

        Usado após deletar evento com sucesso.
        O JavaScript do calendar.js escuta este trigger e
        remove o evento do calendário sem refetch completo.

        Args:
            event_id: ID do evento deletado.

        Returns:
            JsonResponse com ID e header HX-Trigger.
        """
        logger.warning(
            f"Event deleted: event_id={event_id}, " f"user={self.request.user.username}"
        )

        response = JsonResponse({"id": event_id})
        response["HX-Trigger"] = json.dumps({"eventDeleted": {"id": event_id}})
        return response


class EventModalContextMixin(ModalContextMixin):
    """
    Domain-Specific Modal Context Mixin para Event.

    Herda de ModalContextMixin (genérico do core) e pode
    especializar comportamentos específicos do domínio Event,
    se necessário.

    Este mixin fornece contexto para modais de formulário de Event,
    evitando duplicação entre Create/Update views.

    Attributes:
        modal_title: Título do modal.
        submit_button_text: Texto do botão de submit.
    """

    pass


class EventFormLayoutMixin(FormLayoutMixin):
    """
    Domain-Specific Form Layout Mixin para eventos.

    Define o layout estático, ícones e classes (lógica de
    apresentação específica) para o formulário de Event.

    Herda de FormLayoutMixin (genérico do core) e especializa
    os atributos para o domínio de Event.

    Attributes:
        form_class: Classe do formulário Django.
        template_name: Nome do template a ser renderizado.
        form_layout_dict: Dicionário com classes CSS Bootstrap
                         para cada campo.
        default_col_class: Classe CSS padrão para campos
                          não especificados.
        form_icons: Dicionário com ícones Font Awesome para
                   cada campo.
    """

    form_class = EventForm
    template_name = EVENT_FORM_MODAL_TEMPLATE

    form_layout_dict: ClassVar[dict] = {
        "title": "col-md-6",
        "event_type": "col-md-6",
        "location": "col-md-12",
        "description": "col-md-12",
        "start_time_input": "col-md-6",
        "end_time_input": "col-md-6",
    }
    default_col_class = "col-12"
    form_icons: ClassVar[dict] = {
        "title": "fas fa-heading",
        "event_type": "fas fa-tag",
        "location": "fas fa-map-marker-alt",
        "description": "fas fa-align-left",
        "start_time_input": "fas fa-clock",
        "end_time_input": "fas fa-clock",
    }


class EventFormMixin:
    """
    Mixin que configura form_class e campos comuns para CBVs de formulário.
    """

    form_class = EventForm
    template_name = EVENT_FORM_MODAL_TEMPLATE

    def get_event_date(self):
        """
        Obtém a data do evento.

        Pode ser sobrescrito nas views filhas para fornecer lógica específica.
        Por padrão, tenta obter do GET (clicked_date) ou do evento existente.

        Returns:
            date: Data do evento.
        """
        # Para updates, pega a data do evento existente
        if hasattr(self, "object") and self.object and self.object.start_time:
            from django.utils import timezone

            return timezone.localtime(self.object.start_time).date()

        # Para creates, pega do GET (dia clicado no calendário)
        clicked_date_str = self.request.GET.get("date")
        if clicked_date_str:
            from datetime import datetime

            return datetime.strptime(clicked_date_str, "%Y-%m-%d").date()

        return None

    def form_valid(self, form):
        """
        Salva o evento com planner, wedding e combina data + hora.
        """
        from datetime import datetime

        from django.utils import timezone

        event = form.save(commit=False)
        event.planner = self.request.user
        event.wedding = self.wedding

        # Obtém a data do evento
        event_date = self.get_event_date()

        if not event_date:
            logger.error(
                f"Event date not found: wedding_id={self.wedding.id}, "
                f"user={self.request.user.username}"
            )
            # Adiciona erro ao formulário
            form.add_error(None, "Data do evento não encontrada.")
            return self.form_invalid(form)

        # Combina data + hora de início
        start_time_input = form.get_start_time_input()
        if start_time_input:
            event.start_time = timezone.make_aware(
                datetime.combine(event_date, start_time_input)
            )

        # Combina data + hora de fim (opcional)
        end_time_input = form.get_end_time_input()
        if end_time_input:
            event.end_time = timezone.make_aware(
                datetime.combine(event_date, end_time_input)
            )

        event.save()

        logger.info(
            f"Event created/updated: event_id={event.id}, "
            f"title='{event.title}', "
            f"event_type='{event.event_type}', "
            f"start_time={event.start_time}, "
            f"wedding_id={self.wedding.id}, "
            f"user={self.request.user.username}"
        )

        # Retorna resposta com trigger HTMX
        return self.render_event_saved_response()

    def form_invalid(self, form):
        """
        Renderiza o formulário com erros mantendo o contexto do modal.
        """
        logger.warning(
            f"Event form validation failed: "
            f"errors={form.errors.as_json()}, "
            f"user={self.request.user.username}"
        )

        context = self.get_context_data(
            form=form,
            wedding=self.wedding,
            event=getattr(self, "object", None),
        )
        return self.render_to_response(context)
