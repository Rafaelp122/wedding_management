from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from apps.contracts.models import Contract
from apps.core.utils.constants import GRADIENTS
from apps.items.models import Item
from apps.weddings.models import Wedding


class ContractsPartialView(LoginRequiredMixin, TemplateView):
    """
    Exibe a lista de contratos de um casamento,
    injetando um gradiente para cada item.
    """
    template_name = "contracts/contracts_partial.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        wedding_id = self.kwargs.get("wedding_id")

        planner = self.request.user

        wedding = get_object_or_404(Wedding, id=wedding_id, planner=planner)
        context["wedding"] = wedding

        contracts_qs = Contract.objects.filter(
            wedding=wedding
        ).select_related('item', 'supplier')

        context["contracts_list"] = [
            {
                "contract": contract,
                "gradient": GRADIENTS[idx % len(GRADIENTS)]
            }
            for idx, contract in enumerate(contracts_qs)
        ]

        return context
