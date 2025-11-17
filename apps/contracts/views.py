from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from apps.contracts.models import Contract
from apps.core.constants import GRADIENTS
from apps.weddings.models import Wedding


class ContractsPartialView(LoginRequiredMixin, TemplateView):
    """
    Mostra os contratos relacionados a um casamento específico.
    Cada contrato recebe um gradiente para exibição no template.
    """

    template_name = "contracts/contracts_partial.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ID do casamento vindo da URL
        wedding_id = self.kwargs.get("wedding_id")

        # Usuário logado (planner)
        planner = self.request.user

        # Busca o casamento do planner, ou retorna 404 se não existir
        wedding = get_object_or_404(Wedding, id=wedding_id, planner=planner)
        context["wedding"] = wedding

        # Busca os contratos cujo item está relacionado ao casamento
        # select_related otimiza a consulta para buscar o item relacionado
        contracts_qs = Contract.objects.filter(item__wedding=wedding).select_related(
            "item"
        )

        # Cria uma lista de contratos com gradiente associado
        context["contracts_list"] = [
            {"contract": contract, "gradient": GRADIENTS[idx % len(GRADIENTS)]}
            for idx, contract in enumerate(contracts_qs)
        ]

        return context
