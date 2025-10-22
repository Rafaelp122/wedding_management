# Em scheduler/views.py

import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.weddings.models import Wedding # Ajuste o import
from .models import Schedule

@login_required
def partial_scheduler(request, wedding_id):
    """
    Retorna o HTML parcial (snippet) do calendário para ser 
    injetado na aba via HTMX.
    """
    # 1. Encontra o casamento correto
    wedding = get_object_or_404(Wedding, pk=wedding_id)
    
    # 2. Filtra APENAS eventos deste casamento
    events = Schedule.objects.filter(wedding=wedding)
    
    # 3. Formata os dados para o FullCalendar (JSON)
    #    FullCalendar espera chaves 'title', 'start', 'end'
    calendar_events = []
    for event in events:
        calendar_events.append({
            'id': event.id,
            'title': event.title,
            'start': event.start_datetime.isoformat(), # Formato padrão ISO
            'end': event.end_datetime.isoformat(),
            'description': event.description or "",
            # Você pode adicionar mais campos aqui (ex: 'color')
        })

    # 4. Prepara o contexto para o template
    context = {
        'wedding': wedding,
        # Converte a lista de eventos para uma string JSON segura
        'calendar_events_json': json.dumps(calendar_events),
    }
    
    # 5. Renderiza o TEMPLATE PARCIAL
    return render(request, 'scheduler/partials/scheduler_partial.html', context)