from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone

from apps.weddings.models import Wedding
from .models import Event
from .forms import EventForm


@login_required
def event_form(request, wedding_id, event_id=None):
    """
    Exibe o formulário de criação ou edição de evento.
    """
    wedding = get_object_or_404(Wedding, id=wedding_id, planner=request.user)
    instance = None

    if event_id:
        instance = get_object_or_404(Event, id=event_id, planner=request.user)

    clicked_date = request.GET.get("date")

    form = EventForm(
        instance=instance,
        clicked_date=clicked_date,
    )

    context = {
        "form": form,
        "wedding": wedding,
        "is_edit": instance is not None,
    }

    return render(request, "scheduler/partials/_event_form.html", context)


@login_required
def event_save(request, wedding_id, event_id=None):
    """
    Salva o evento criado ou editado via HTMX.
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
        event.start_time = timezone.make_aware(
            timezone.datetime.fromisoformat(form.cleaned_data["start_time"])
        )
        if form.cleaned_data.get("end_time"):
            event.end_time = timezone.make_aware(
                timezone.datetime.fromisoformat(form.cleaned_data["end_time"])
            )
        event.save()

        # Após salvar, fecha o modal e atualiza o calendário
        response = HttpResponse(status=204)
        response["HX-Trigger"] = "eventUpdated"
        response["HX-Trigger-After-Settle"] = "closeModal"
        return response

    # Se inválido, re-renderiza o form com erros
    return render(
        request, "scheduler/partials/_event_form.html", {"form": form, "wedding": wedding}
    )
