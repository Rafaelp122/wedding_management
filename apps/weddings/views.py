from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView, UpdateView

from apps.budget.forms import BudgetForm

# Imports de apps
from apps.client.forms import ClientForm
from apps.client.models import Client
from apps.users.models import User

# Import do decorator personalizado
from .decorators import planner_required
from .forms import WeddingForm
from .models import Wedding

# Constante para os gradientes dos cards
GRADIENTS = [
    "linear-gradient(135deg, #8e2de2, #4a00e0)",
    "linear-gradient(135deg, #7b1fa2, #512da8)",
    "linear-gradient(135deg, #e91e63, #ff6f61)",
    "linear-gradient(135deg, #009688, #00695c)",
    "linear-gradient(135deg, #3f51b5, #1a237e)",
    "linear-gradient(135deg, #ff9800, #ef6c00)",
    "linear-gradient(135deg, #2196f3, #0d47a1)",
    "linear-gradient(135deg, #4caf50, #1b5e20)",
    "linear-gradient(135deg, #f44336, #b71c1c)",
    "linear-gradient(135deg, #ffeb3b, #fbc02d)",
    "linear-gradient(135deg, #00bcd4, #00838f)",
    "linear-gradient(135deg, #9c27b0, #4a148c)",
    "linear-gradient(135deg, #cddc39, #827717)",
    "linear-gradient(135deg, #795548, #3e2723)",
    "linear-gradient(135deg, #607d8b, #263238)",
    "linear-gradient(135deg, #673ab7, #311b92)",
    "linear-gradient(135deg, #ff5722, #bf360c)",
    "linear-gradient(135deg, #03a9f4, #01579b)",
    "linear-gradient(135deg, #76ff03, #33691e)",
]

# --- Mixin para reutilização de lógica nas CBVs ---


class PlannerOwnerMixin:
    """ Mixin que filtra os resultados para mostrar apenas os dados do planner logado. """
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(planner=self.request.user)

# --- Class-Based Views (CBVs) para CRUD ---


class WeddingListView(LoginRequiredMixin, PlannerOwnerMixin, ListView):
    model = Wedding
    template_name = "weddings/list.html"
    context_object_name = "weddings"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        weddings = self.get_queryset().select_related("client")
        context["weddings_with_clients"] = [
            {
                "wedding": wedding,
                "client": wedding.client,
                "gradient": GRADIENTS[idx % len(GRADIENTS)],
            }
            for idx, wedding in enumerate(weddings)
        ]
        return context


class WeddingDetailView(LoginRequiredMixin, PlannerOwnerMixin, DetailView):
    model = Wedding
    template_name = "weddings/detail.html"
    context_object_name = "wedding"
    pk_url_kwarg = 'wedding_id'


class WeddingUpdateView(LoginRequiredMixin, PlannerOwnerMixin, UpdateView):
    model = Wedding
    form_class = WeddingForm
    template_name = "weddings/edit.html"
    success_url = reverse_lazy("weddings:my_weddings")
    pk_url_kwarg = 'id'


class WeddingDeleteView(LoginRequiredMixin, PlannerOwnerMixin, DeleteView):
    model = Wedding
    template_name = "weddings/confirm_delete.html" # Requer um template de confirmação
    success_url = reverse_lazy("weddings:my_weddings")
    pk_url_kwarg = 'id'

# --- View de Função para o fluxo de criação com HTMX ---


@planner_required
def create_wedding_flow(request):
    """ View para o fluxo de criação de casamento em múltiplos passos com HTMX. """
    planner = request.planner  # O decorator já injetou o planner aqui

    if request.htmx:
        step = request.POST.get("step")

        if step == "client":
            form = ClientForm(request.POST)
            if form.is_valid():
                request.session["new_wedding_client_data"] = form.cleaned_data
                return render(
                    request,
                    "weddings/partials/form-wedding-and-budget.html",
                    {"wedding_form": WeddingForm(), "budget_form": BudgetForm()},
                )
            return render(request, "weddings/partials/form-client.html", {"form": form})

        elif step == "wedding_and_budget":
            client_data = request.session.get("new_wedding_client_data")
            if not client_data:
                response = HttpResponse()
                response["HX-Redirect"] = reverse("weddings:create_wedding_flow")
                return response

            wedding_form = WeddingForm(request.POST)
            budget_form = BudgetForm(request.POST)

            if wedding_form.is_valid() and budget_form.is_valid():
                with transaction.atomic():  # Garante a integridade dos dados
                    client = Client.objects.create(**client_data)

                    wedding = wedding_form.save(commit=False)
                    wedding.planner = planner
                    wedding.client = client
                    wedding.save()

                    budget = budget_form.save(commit=False)
                    budget.planner = planner
                    budget.wedding = wedding
                    budget.save()

                del request.session["new_wedding_client_data"]
                response = HttpResponse()
                response["HX-Redirect"] = reverse("weddings:my_weddings")
                return response

            return render(
                request,
                "weddings/partials/form-wedding-and-budget.html",
                {"wedding_form": wedding_form, "budget_form": budget_form},
            )

    # Limpa a sessão em caso de um GET inicial para recomeçar o fluxo
    if "new_wedding_client_data" in request.session:
        del request.session["new_wedding_client_data"]

    return render(request, "weddings/create-flow.html", {"form": ClientForm()})
