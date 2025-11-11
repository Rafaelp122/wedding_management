import json
from datetime import datetime
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone

from apps.weddings.models import Wedding
from .models import Event
from .forms import EventForm


# ============================================================
# FORMULÁRIO DE CRIAÇÃO / EDIÇÃO DE EVENTOS
# ============================================================
@login_required
def event_form(request, wedding_id, event_id=None):
    """
    Exibe o formulário HTMX para criar ou editar um evento.
    """
    wedding = get_object_or_404(Wedding, id=wedding_id, planner=request.user)
    instance = None

    if event_id:
        instance = get_object_or_404(Event, id=event_id, planner=request.user)

    clicked_date = request.GET.get("date")

    form = EventForm(instance=instance, clicked_date=clicked_date)

    context = {
        "form": form,
        "wedding": wedding,
        "is_edit": instance is not None,
        "event": instance,
    }

    return render(request, "scheduler/partials/_event_form.html", context)


# ============================================================
# SALVAR EVENTO (CRIAÇÃO / EDIÇÃO)
# ============================================================
@login_required
def event_save(request, wedding_id, event_id=None):
    """
    Cria ou atualiza um evento, retornando JSON reativo via HTMX.
    """
    wedding = get_object_or_404(Wedding, id=wedding_id, planner=request.user)
    instance = None

    if event_id:
        instance = get_object_or_404(Event, id=event_id, planner=request.user)

    form = EventForm(request.POST, instance=instance)

    if form.is_valid():
        event = form.save(commit=False)
        event.planner = request.user
        event.wedding = wedding

        # Combina data e hora
        event_date = form.cleaned_data.get("event_date")
        start_time_input = form.cleaned_data.get("start_time_input")
        end_time_input = form.cleaned_data.get("end_time_input")

        if event_date and start_time_input:
            event.start_time = timezone.make_aware(datetime.combine(event_date, start_time_input))
        if event_date and end_time_input:
            event.end_time = timezone.make_aware(datetime.combine(event_date, end_time_input))

        event.save()

        # 🔹 Prepara o JSON do evento para HTMX
        data = {
            "id": event.id,
            "title": event.title,
            "start": event.start_time.isoformat(),
            "end": event.end_time.isoformat() if event.end_time else None,
            "description": event.description,
            "event_type": event.event_type,
        }

        # 🔹 Define o tipo de trigger
        trigger_type = "eventUpdated" if instance else "eventCreated"

        response = JsonResponse(data)
        response["HX-Trigger"] = json.dumps({trigger_type: data})
        return response

    # ❌ Se o form for inválido, re-renderiza o formulário
    return render(
        request,
        "scheduler/partials/_event_form.html",
        {"form": form, "wedding": wedding, "is_edit": event_id is not None},
    )


# ============================================================
# EXCLUIR EVENTO
# ============================================================
@login_required
def event_delete(request, wedding_id, event_id):
    """
    Exclui um evento via HTMX e notifica o calendário.
    """
    event = get_object_or_404(Event, id=event_id, planner=request.user)

    if request.method == "POST":
        event_id = event.id
        event.delete()

        # 🔹 Retorna trigger reativo de deleção
        response = JsonResponse({"id": event_id})
        response["HX-Trigger"] = json.dumps({"eventDeleted": {"id": event_id}})
        return response

    # Se for GET, exibe o modal de confirmação
    return render(
        request,
        "scheduler/partials/_event_delete_confirm.html",
        {"event": event, "wedding_id": wedding_id},
    )
