
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from apps.scheduler.models import Schedule  # ou o model que usar pra eventos
from apps.users.models import User
from apps.weddings.models import Wedding


@login_required
def partial_scheduler(request, wedding_id):
    planner = request.user
    wedding = get_object_or_404(Wedding, id=wedding_id, planner=planner)

    events = Schedule.objects.filter(wedding=wedding)

    context = {
        "wedding": wedding,
        "events": events,
    }

    return render(request, "scheduler/scheduler_partial.html", context)
