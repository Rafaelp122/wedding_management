# apps/budget/views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from apps.users.models import Planner
from apps.items.models import Item
from apps.weddings.models import Wedding

@login_required
def budget_detail(request, id):
    planner = Planner.objects.get(user=request.user)
    wedding = get_object_or_404(Wedding, id=id, planner=planner)

    itens = Item.objects.filter(budget__wedding=wedding)

    orcamento_total = 85000
    gasto_atual = 52300
    saldo_disponivel = orcamento_total - gasto_atual

    gastos_distribuidos = {
        "Local e Buffet": 35000,
        "Decoração": 15000,
        "Fotografia e Vídeo": 10000,
        "Vestuário": 12000,
    }

    context = {
        "wedding": wedding,
        "itens": itens,
        "orcamento_total": orcamento_total,
        "gasto_atual": gasto_atual,
        "saldo_disponivel": saldo_disponivel,
        "gastos_distribuidos": gastos_distribuidos,
    }

    return render(request, "weddings/detail.html", context)
