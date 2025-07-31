from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.db.models import Sum, F, ExpressionWrapper, DecimalField

from apps.users.models import Planner
from apps.items.models import Item
from apps.weddings.models import Wedding

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.db.models import Sum, F, ExpressionWrapper, DecimalField


@login_required
def partial_budget(request, wedding_id):
    # Pega o planner relacionado ao usuário logado
    planner = Planner.objects.get(user=request.user)

    # Busca o casamento pelo id e planner, ou retorna 404 se não achar
    wedding = get_object_or_404(Wedding, id=wedding_id, planner=planner)

    # Obtém o orçamento relacionado ao casamento, ou None se não existir
    budget = getattr(wedding, 'budget', None)

    if not budget:
        total_budget = 0  # Orçamento total
        items = Item.objects.none()  # Queryset vazio caso não tenha orçamento
    else:
        total_budget = budget.initial_estimate  # Estimativa inicial do orçamento
        items = Item.objects.filter(budget=budget)  # Itens relacionados a esse orçamento

    # Calcula o gasto atual somando unit_price * quantity de todos os itens
    current_spent = items.aggregate(
        total=Sum(
            ExpressionWrapper(
                F('unit_price') * F('quantity'),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        )
    )['total'] or 0

    # Calcula o saldo disponível subtraindo gasto atual do orçamento total
    available_balance = total_budget - current_spent

    # Gastos distribuídos de exemplo (fixos)
    distributed_expenses = {
        "Local e Buffet": 35000,
        "Decoração": 15000,
        "Fotografia e Vídeo": 10000,
        "Vestuário": 12000,
    }

    # Prepara o contexto para renderizar o template
    context = {
        "wedding": wedding,
        "items": items,
        "total_budget": total_budget,
        "current_spent": current_spent,
        "available_balance": available_balance,
        "distributed_expenses": distributed_expenses,
    }

    return render(request, "budget/budget_overview.html", context)
