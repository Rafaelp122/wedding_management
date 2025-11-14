import json
from datetime import datetime
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.utils import timezone
from django.views import View
from django.urls import reverse

from .models import Event
from .forms import EventForm
from .mixins import SchedulerWeddingMixin

# FORMULÁRIO DE EVENTO (criar/editar)

class EventFormView(SchedulerWeddingMixin, View):
    """
    Exibe o formulário de criação ou edição de um evento.
    """
    form_class = EventForm
    template_name = "scheduler/partials/_event_form.html"

    def get(self, request, *args, **kwargs):
        event_id = self.kwargs.get("event_id")
        instance = None

        if event_id:
            instance = get_object_or_404(
                Event, id=event_id,
                planner=request.user
            )

        clicked_date = request.GET.get("date")
        form = self.form_class(instance=instance, clicked_date=clicked_date)

        # Define URL correta do form (create/update)
        if instance:
            form_action = reverse(
                "scheduler:event_update",
                args=[self.wedding.id, instance.id]
            )
        else:
            form_action = reverse("scheduler:event_save", args=[self.wedding.id])

        context = {
            "form": form,
            "form_action": form_action,
            "wedding": self.wedding,
            "is_edit": instance is not None,
            "event": instance,
        }
        return render(request, self.template_name, context)

# SALVAMENTO DO EVENTO

class EventSaveView(SchedulerWeddingMixin, View):
    """
    Processa requisições POST para criar ou atualizar eventos.
    """
    form_class = EventForm
    template_name = "scheduler/partials/_event_form.html"

    def post(self, request, *args, **kwargs):
        event_id = self.kwargs.get("event_id")
        instance = None

        if event_id:
            instance = get_object_or_404(
                Event,
                id=event_id,
                planner=request.user
            )

        form = self.form_class(request.POST, instance=instance)

        if form.is_valid():
            event = form.save(commit=False)
            event.planner = request.user
            event.wedding = self.wedding

            event_date = form.cleaned_data.get("event_date")
            start_time_input = form.cleaned_data.get("start_time_input")
            end_time_input = form.cleaned_data.get("end_time_input")

            if event_date and start_time_input:
                event.start_time = timezone.make_aware(
                    datetime.combine(event_date, start_time_input)
                )
            if event_date and end_time_input:
                event.end_time = timezone.make_aware(
                    datetime.combine(event_date, end_time_input)
                )

            event.save()

            data = {
                "id": event.id,
                "title": event.title,
                "start": event.start_time.isoformat(),
                "end": event.end_time.isoformat() if event.end_time else None,
                "description": event.description,
                "event_type": event.event_type,
            }

            trigger_type = "eventUpdated" if instance else "eventCreated"

            response = JsonResponse(data)
            response["HX-Trigger-After-Settle"] = json.dumps({
                trigger_type: data,
                "closeModal": True
            })
            return response

        # Caso inválido → reexibe modal com erros
        context = {
            "form": form,
            "wedding": self.wedding,
            "is_edit": instance is not None,
            "event": instance,
        }
        return render(request, self.template_name, context)


# ABRIR MODAL DE CONFIRMAÇÃO (GENÉRICO)

class EventDeleteModalView(SchedulerWeddingMixin, View):

    template_name = "partials/confirm_delete_modal.html"

    def get(self, request, *args, **kwargs):
        event = get_object_or_404(
            Event,
            id=kwargs["event_id"],
            planner=request.user,
            wedding=self.wedding
        )

        context = {
            "hx_post_url": reverse(
                "scheduler:event_delete",
                args=[self.wedding.id, event.id]
            ),
            "hx_target_id": "#form-modal-container",
            "object_type": "o evento",
            "object_name": event.title,
        }

        return render(request, self.template_name, context)
   
# EXECUTAR EXCLUSÃO

class EventDeleteView(SchedulerWeddingMixin, View):
    """
    Deleta o evento e retorna JSON com trigger HTMX.
    """

    def post(self, request, *args, **kwargs):
        event = get_object_or_404(
            Event,
            id=kwargs["event_id"],
            planner=request.user,
            wedding=self.wedding
        )

        event_id = event.id
        event.delete()

        response = JsonResponse({"id": event_id})
        response["HX-Trigger"] = json.dumps({"eventDeleted": {"id": event_id}})
        return response
