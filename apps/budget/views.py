from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.db.models import Sum, F, ExpressionWrapper, DecimalField

from apps.users.models import Planner
from apps.items.models import Item
from apps.weddings.models import Wedding

class BudgetPartialView(LoginRequiredMixin, TemplateView):
    template_name = "budget/budget_overview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        wedding_id = self.kwargs.get('wedding_id')
        
        planner = get_object_or_404(Planner, user=self.request.user)
        
        wedding = get_object_or_404(Wedding, id=wedding_id, planner=planner)
        context['wedding'] = wedding

        budget = getattr(wedding, 'budget', None)

        if not budget:
            total_budget = 0
            items = Item.objects.none()
        else:
            total_budget = budget.initial_estimate
            items = Item.objects.filter(wedding=wedding)
        
        context['items'] = items
        context['total_budget'] = total_budget

        current_spent = items.aggregate(
            total=Sum(
                ExpressionWrapper(
                    F('unit_price') * F('quantity'),
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                )
            )
        )['total'] or 0
        context['current_spent'] = current_spent

        available_balance = total_budget - current_spent
        context['available_balance'] = available_balance

        category_expenses_query = items.values('category').annotate(
            total_cost=Sum(
                ExpressionWrapper(
                    F('unit_price') * F('quantity'),
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                )
            )
        ).order_by('-total_cost')

        distributed_expenses = {
            item['category']: item['total_cost']
            for item in category_expenses_query
        }
        
        category_display_map = dict(Item.CATEGORY_CHOICES)
        context['distributed_expenses'] = {
            category_display_map.get(cat, cat): cost
            for cat, cost in distributed_expenses.items()
        }

        return context