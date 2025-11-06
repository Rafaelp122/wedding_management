from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from apps.core.utils.constants import GRADIENTS
from apps.items.models import Item
from apps.weddings.models import Wedding


class BudgetPartialView(LoginRequiredMixin, TemplateView):
    template_name = "budget/budget_overview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        wedding_id = self.kwargs.get("wedding_id")
        planner = self.request.user

        wedding = get_object_or_404(Wedding, id=wedding_id, planner=planner)
        context["wedding"] = wedding

        items = Item.objects.filter(wedding=wedding)

        total_budget = wedding.budget
        current_spent = items.total_spent()

        context["total_budget"] = total_budget
        context["items"] = items
        context["current_spent"] = current_spent
        context["available_balance"] = total_budget - current_spent

        category_expenses_query = items.category_expenses()

        distributed_expenses_dict = {
            item["category"]: item["total_cost"] for item in category_expenses_query
        }

        category_display_map = dict(Item.CATEGORY_CHOICES)
        distributed_expenses_with_names = {
            category_display_map.get(cat, cat): cost
            for cat, cost in distributed_expenses_dict.items()
        }

        context["distributed_expenses"] = [
            {
                "category": cat,
                "value": cost,
                "gradient": GRADIENTS[idx % len(GRADIENTS)]
            }
            for idx, (cat, cost) in enumerate(distributed_expenses_with_names.items())
        ]

        return context
