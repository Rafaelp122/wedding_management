from django.shortcuts import get_object_or_404
from django.http import JsonResponse, Http404
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from ..models import Event
from apps.weddings.models import Wedding


@login_required
def event_api(request, wedding_id):
    """Retorna os eventos e casamentos do planner logado em formato JSON para o calendário."""
    planner = request.user

    # Busca e valida o casamento atual pertencente ao planner
    try:
        current_wedding = get_object_or_404(Wedding, pk=wedding_id, planner=planner)
    except Http404:
        return JsonResponse(
            {"error": "Casamento inválido ou não autorizado."}, status=403
        )

    # Busca todos os eventos e casamentos vinculados ao planner
    all_events = Event.objects.filter(planner=planner)
    all_weddings = Wedding.objects.filter(planner=planner)

    calendar_events = []  # Lista que conterá os eventos formatados

    # Adiciona os dias de casamento ao calendário
    for w in all_weddings:
        is_current = w.id == current_wedding.id
        wedding_title = (
            f"{w.groom_name} & {w.bride_name}"
            if w.groom_name and w.bride_name
            else (w.client.name if w.client else "Casamento")
        )
        calendar_events.append(
            {
                "title": wedding_title,
                "start": w.date.isoformat(),
                "allDay": True,
                "display": "background",
                "color": "#ffc107",  # Amarelo Bootstrap
                "extendedProps": {"isWeddingDay": True, "isCurrentWedding": is_current},
            }
        )

    # Adiciona os eventos individuais do planner
    for event in all_events:
        is_current_w_event = event.wedding_id == current_wedding.id
        calendar_events.append(
            {
                "id": event.id,
                "title": event.title,
                "start": (
                    timezone.localtime(event.start_time).isoformat()
                    if event.start_time
                    else None
                ),
                "end": (
                    timezone.localtime(event.end_time).isoformat()
                    if event.end_time
                    else None
                ),
                "allDay": False,
                "extendedProps": {
                    "isWeddingDay": False,
                    "isCurrentWedding": is_current_w_event,
                    "description": event.description or "",
                    "location": event.location or "",
                    "type": event.get_event_type_display() or "",
                },
            }
        )

    # Retorna os dados como JSON
    return JsonResponse(calendar_events, safe=False)
