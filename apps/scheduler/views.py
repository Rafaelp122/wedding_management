# scheduler/views.py

import json
from datetime import datetime
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.utils import timezone
from django.views import View
from django.views.generic import DeleteView

from .models import Event
from .forms import EventForm
from .mixins import SchedulerWeddingMixin  # Importa o Mixin responsável por garantir contexto do casamento


class EventFormView(SchedulerWeddingMixin, View):
    """
    Exibe o formulário de criação ou edição de um evento.
    Substitui a antiga função 'event_form'.
    """
    form_class = EventForm
    template_name = "scheduler/partials/_event_form.html"

    def get(self, request, *args, **kwargs):
        event_id = self.kwargs.get("event_id")
        instance = None

        # Caso o evento exista, busca-o garantindo que pertença ao planner logado
        if event_id:
            instance = get_object_or_404(Event, id=event_id, planner=request.user)

        # Caso o usuário tenha clicado em uma data específica no calendário
        clicked_date = request.GET.get("date")

        form = self.form_class(
            instance=instance,
            clicked_date=clicked_date
        )

        context = {
            "form": form,
            "wedding": self.wedding,  # Atributo herdado do Mixin
            "is_edit": instance is not None,
            "event": instance,
        }
        return render(request, self.template_name, context)


class EventSaveView(SchedulerWeddingMixin, View):
    """
    Processa requisições POST para criar ou atualizar eventos.
    Substitui a antiga função 'event_save'.
    """
    form_class = EventForm
    template_name = "scheduler/partials/_event_form.html"  # Reutilizado para exibir erros de validação

    def post(self, request, *args, **kwargs):
        event_id = self.kwargs.get("event_id")
        instance = None

        # Recupera o evento se for uma edição
        if event_id:
            instance = get_object_or_404(Event, id=event_id, planner=request.user)

        form = self.form_class(request.POST, instance=instance)

        if form.is_valid():
            event = form.save(commit=False)
            event.planner = request.user
            event.wedding = self.wedding  # Obtido via Mixin

            # Combina a data e as horas em objetos datetime com fuso horário
            event_date = form.cleaned_data.get("event_date")
            start_time_input = form.cleaned_data.get("start_time_input")
            end_time_input = form.cleaned_data.get("end_time_input")

            if event_date and start_time_input:
                event.start_time = timezone.make_aware(datetime.combine(event_date, start_time_input))
            if event_date and end_time_input:
                event.end_time = timezone.make_aware(datetime.combine(event_date, end_time_input))

            event.save()

            # Estrutura de resposta para o HTMX atualizar o calendário dinamicamente
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
            response["HX-Trigger"] = json.dumps({trigger_type: data})
            return response

        # Caso o formulário seja inválido, reexibe o formulário com erros
        context = {
            "form": form,
            "wedding": self.wedding,
            "is_edit": instance is not None,
            "event": instance,
        }
        return render(request, self.template_name, context)


class EventDeleteView(SchedulerWeddingMixin, DeleteView):
    """
    Responsável por exibir a confirmação e processar a exclusão de eventos.
    Substitui a antiga função 'event_delete'.
    """
    model = Event
    template_name = "scheduler/partials/_event_delete_confirm.html"
    pk_url_kwarg = "event_id"  # Relaciona o parâmetro da URL ao campo primário

    def get_queryset(self):
        """
        Restringe a exclusão apenas a eventos pertencentes ao planner autenticado
        e ao casamento em contexto.
        """
        return self.model.objects.filter(
            planner=self.request.user,
            wedding=self.wedding
        )

    def get_context_data(self, **kwargs):
        """
        Inclui o ID do casamento no contexto do template de confirmação.
        """
        context = super().get_context_data(**kwargs)
        context["wedding_id"] = self.wedding.id
        return context

    def delete(self, request, *args, **kwargs):
        """
        Sobrescreve o método padrão para retornar uma resposta JSON
        com o evento deletado, disparando um trigger HTMX.
        """
        self.object = self.get_object()
        event_id = self.object.id
        self.object.delete()

        response = JsonResponse({"id": event_id})
        response["HX-Trigger"] = json.dumps({"eventDeleted": {"id": event_id}})
        return response

    def post(self, request, *args, **kwargs):
        """
        O método DeleteView padrão chama 'delete()';
        aqui ele é invocado diretamente para manter consistência na resposta.
        """
        return self.delete(request, *args, **kwargs)
