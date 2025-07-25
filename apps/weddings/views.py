from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.users.models import Planner
from apps.items.models import Item
from apps.client.models import Client
from .forms import WeddingForm
from .models import Wedding

from django.urls import reverse
from django.http import HttpResponse
from apps.client.forms import ClientForm

from apps.budget.forms import BudgetForm


# Lista de degradês para os cards
GRADIENTS = [
    "linear-gradient(135deg, #8e2de2, #4a00e0)",
    "linear-gradient(135deg, #7b1fa2, #512da8)",
    "linear-gradient(135deg, #e91e63, #ff6f61)",
    "linear-gradient(135deg, #009688, #00695c)",
    "linear-gradient(135deg, #3f51b5, #1a237e)",
    "linear-gradient(135deg, #ff9800, #ef6c00)",
]


@login_required
def my_weddings(request):
    planner = Planner.objects.get(user=request.user)

    weddings = Wedding.objects.filter(planner=planner).select_related("client")

    weddings_with_gradients = []
    for idx, wedding in enumerate(weddings):
        gradient = GRADIENTS[idx % len(GRADIENTS)]
        weddings_with_gradients.append(
            {
                "wedding": wedding,
                "client": wedding.client,
                "gradient": gradient,
            }
        )

    return render(
        request,
        "weddings/list.html",
        {"weddings_with_clients": weddings_with_gradients},
    )


@login_required
def create_wedding_flow(request):
    try:
        planner = Planner.objects.get(user=request.user)
    except Planner.DoesNotExist:
        return HttpResponse("Acesso negado", status=403)

    if request.htmx:
        step = request.POST.get("step")

        if step == "client":
            form = ClientForm(request.POST)
            if form.is_valid():
                request.session["new_wedding_client_data"] = form.cleaned_data

                wedding_form = WeddingForm()
                budget_form = BudgetForm()

                return render(
                    request,
                    "weddings/partials/form-wedding-and-budget.html",
                    {"wedding_form": wedding_form, "budget_form": budget_form},
                )
            else:
                return render(
                    request, "weddings/partials/form-client.html", {"form": form}
                )

        elif step == "wedding_and_budget":
            client_data = request.session.get("new_wedding_client_data")

            wedding_form = WeddingForm(request.POST)
            budget_form = BudgetForm(request.POST)

            if not client_data:
                # Lógica de segurança para sessão expirada
                response = HttpResponse()
                response["HX-Redirect"] = reverse("weddings:create_wedding_flow")
                return response

            # Verifique se AMBOS são válidos
            if wedding_form.is_valid() and budget_form.is_valid():

                # Primeiro, crie o Cliente
                new_client = Client.objects.create(**client_data)

                # Segundo, crie o Casamento
                wedding = wedding_form.save(commit=False)
                wedding.planner = planner
                wedding.client = new_client
                wedding.save()  # Salva para obter um ID

                # Terceiro, crie o Orçamento e o associe
                budget = budget_form.save(commit=False)
                budget.planner = planner
                budget.wedding = wedding  # Associa ao casamento recém-criado
                budget.save()

                # Limpe a sessão e redirecione
                del request.session["new_wedding_client_data"]
                response = HttpResponse()
                response["HX-Redirect"] = reverse("weddings:my_weddings")
                return response
            else:
                # Se um dos formulários for inválido, reenvie a Etapa 2 com os erros
                return render(
                    request,
                    "weddings/partials/form-wedding-and-budget.html",
                    {"wedding_form": wedding_form, "budget_form": budget_form},
                )

    # Para o primeiro acesso (GET)
    if "new_wedding_client_data" in request.session:
        del request.session["new_wedding_client_data"]
    client_form = ClientForm()
    return render(request, "weddings/create-flow.html", {"form": client_form})


@login_required
def edit_wedding(request, id):
    planner = Planner.objects.get(user=request.user)
    wedding = get_object_or_404(Wedding, id=id, planner=planner)

    if request.method == "POST":
        form = WeddingForm(request.POST, instance=wedding)
        if form.is_valid():
            form.save()
            return redirect("weddings:my_weddings")
    else:
        form = WeddingForm(instance=wedding)

    return render(
        request,
        "weddings/create.html",
        {"form": form, "wedding": wedding},
    )


@login_required
@require_POST
def delete_wedding(request, id):
    planner = Planner.objects.get(user=request.user)
    wedding = get_object_or_404(Wedding, id=id, planner=planner)
    wedding.delete()
    return redirect("weddings:my_weddings")


