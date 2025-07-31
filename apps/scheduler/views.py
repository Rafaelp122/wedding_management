
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from apps.users.models import Planner
from apps.weddings.models import Wedding
from apps.scheduler.models import Schedule  # ou o model que usar pra eventos


@login_required
def partial_scheduler(request, wedding_id):
    planner = Planner.objects.get(user=request.user)
    wedding = get_object_or_404(Wedding, id=wedding_id, planner=planner)

    events = Schedule.objects.filter(wedding=wedding)

    context = {
        "wedding": wedding,
        "events": events,
    }

    return render(request, "scheduler/scheduler_partial.html", context)
