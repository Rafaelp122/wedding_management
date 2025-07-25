# apps/budget/views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from apps.users.models import Planner
from apps.items.models import Item
from apps.weddings.models import Wedding

from django.db.models import Sum
from django.db.models import F, ExpressionWrapper, DecimalField

@login_required
def budget_detail(request, id):
    planner = Planner.objects.get(user=request.user)
    wedding = get_object_or_404(Wedding, id=id, planner=planner)

    # Pega o orçamento relacionado ao casamento
    budget = getattr(wedding, 'budget', None)

    if not budget:
        # Se orçamento não existir para esse casamento, trate como quiser:
        orcamento_total = 0
    else:
        orcamento_total = budget.initial_estimate  # ou budget.final_value, conforme seu fluxo

    itens = Item.objects.filter(budget=budget) if budget else Item.objects.none()


    gasto_atual = itens.aggregate(
        total=Sum(
            ExpressionWrapper(
                F('unit_price') * F('quantity'),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        )
    )['total'] or 0
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
