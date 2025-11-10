from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from apps.core.utils.constants import GRADIENTS
from apps.items.models import Item
from apps.weddings.models import Wedding


class BudgetPartialView(LoginRequiredMixin, TemplateView):
    """
    Exibe a visão parcial do orçamento de um casamento específico.
    Acesso restrito ao planejador logado.
    """

    template_name = "budget/budget_overview.html"

    def get_context_data(self, **kwargs):
        """
        Adiciona ao contexto as informações de orçamento,
        itens e distribuição de gastos por categoria.
        """
        context = super().get_context_data(**kwargs)

        # Obtém o ID do casamento a partir da URL
        wedding_id = self.kwargs.get("wedding_id")

        # Usuário autenticado (planner)
        planner = self.request.user

        # Busca o casamento pertencente ao planner; retorna 404 se não existir
        wedding = get_object_or_404(Wedding, id=wedding_id, planner=planner)
        context["wedding"] = wedding

        # Itens associados ao casamento
        items = Item.objects.filter(wedding=wedding)

        # Calcula o total e o gasto atual
        total_budget = wedding.budget
        current_spent = items.total_spent()  # Método customizado no model Item

        # Valores principais do orçamento
        context["total_budget"] = total_budget
        context["items"] = items
        context["current_spent"] = current_spent
        context["available_balance"] = total_budget - current_spent

        # Consulta de despesas por categoria (query agregada)
        category_expenses_query = items.category_expenses()

        # Converte o resultado em dicionário {categoria: custo_total}
        distributed_expenses_dict = {
            item["category"]: item["total_cost"] for item in category_expenses_query
        }

        # Mapeia o valor da categoria para o nome legível (choices)
        category_display_map = dict(Item.CATEGORY_CHOICES)
        distributed_expenses_with_names = {
            category_display_map.get(cat, cat): cost
            for cat, cost in distributed_expenses_dict.items()
        }

        # Prepara os dados para o gráfico ou cards (com gradiente visual)
        context["distributed_expenses"] = [
            {
                "category": cat,
                "value": cost,
                "gradient": GRADIENTS[idx % len(GRADIENTS)],
            }
            for idx, (cat, cost) in enumerate(distributed_expenses_with_names.items())
        ]

        return context
