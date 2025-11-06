from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from apps.contracts.models import Contract
from apps.weddings.models import Wedding


@login_required
def partial_contracts(request, wedding_id):
    planner = request.user
    wedding = get_object_or_404(Wedding, id=wedding_id, planner=planner)

    contracts = Contract.objects.filter(wedding=wedding)

    context = {
        "wedding": wedding,
        "contracts": contracts,
    }

    return render(request, "contracts/contracts_partial.html", context)
