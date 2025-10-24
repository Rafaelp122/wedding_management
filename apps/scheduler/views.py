# Em scheduler/views.py

import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.weddings.models import Wedding 
from .models import Schedule

@login_required
def partial_scheduler(request, wedding_id):

    wedding = get_object_or_404(Wedding, pk=wedding_id)
    
    events = Schedule.objects.filter(wedding=wedding)
    calendar_events = []
    for event in events:
        calendar_events.append({
            'id': event.id,
            'title': event.title,
            'start': event.start_datetime.isoformat(), 
            'end': event.end_datetime.isoformat(),
            'description': event.description or "",
        })

    context = {
        'wedding': wedding,
        'calendar_events_json': json.dumps(calendar_events),
    }
    
    return render(request, 'scheduler/partials/scheduler_partial.html', context)