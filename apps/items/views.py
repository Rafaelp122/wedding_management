from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from apps.users.models import Planner
from apps.weddings.models import Wedding
from apps.items.models import Item


@login_required
def partial_items(request, wedding_id):
    planner = Planner.objects.get(user=request.user)
    wedding = get_object_or_404(Wedding, id=wedding_id, planner=planner)

    items = Item.objects.filter(wedding=wedding)  # ou por budget se preferir

    context = {
        "wedding": wedding,
        "items": items,
    }

    return render(request, "items/items_partial.html", context)
