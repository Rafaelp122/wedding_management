from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from apps.core.constants import GRADIENTS
from apps.items.models import Item
from apps.weddings.models import Wedding


class BudgetPartialView(LoginRequiredMixin, TemplateView):
    """
    Exibe a visão parcial do orçamento de um casamento específico.
    Acesso restrito ao planejador logado.
    """

    template_name = "budget/budget_overview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        wedding_id = self.kwargs.get("wedding_id")

        # Segurança: Garante que o casamento pertence ao usuário logado
        wedding = get_object_or_404(Wedding, id=wedding_id, planner=self.request.user)
        context["wedding"] = wedding

        # QuerySet Base
        items = Item.objects.filter(wedding=wedding)

        # 1. Cálculos Financeiros Gerais
        total_budget = wedding.budget
        current_spent = items.total_spent()  # Retorna Decimal ou 0

        context["total_budget"] = total_budget
        context["items"] = items
        context["current_spent"] = current_spent
        context["available_balance"] = total_budget - current_spent

        # 2. Distribuição por Categoria
        # category_expenses() já retorna ordenado pelo maior gasto
        category_expenses_query = items.category_expenses()

        # Cria um mapa {Código: Nome Legível} para exibição (ex: "DECOR" -> "Decoração")
        category_display_map = dict(Item.CATEGORY_CHOICES)

        # Monta a lista final para o template em uma única iteração
        # Preservando a ordem do QuerySet
        context["distributed_expenses"] = [
            {
                # Pega o nome legível ou usa o código se falhar
                "category": category_display_map.get(entry["category"], entry["category"]),
                "value": entry["total_cost"],
                "gradient": GRADIENTS[idx % len(GRADIENTS)],
            }
            for idx, entry in enumerate(category_expenses_query)
        ]

        return context
