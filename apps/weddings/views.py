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
        step = request.POST.get('step')

        # Etapa 1: Validação do Cliente
        if step == 'client':
            form = ClientForm(request.POST)
            if form.is_valid():
                request.session['new_wedding_client_data'] = form.cleaned_data
                wedding_form = WeddingForm()
                return render(
                    request,
                    'weddings/partials/form-wedding.html',
                    {'form': wedding_form}
                )
            else:
                return render(
                    request,
                    'weddings/partials/form-client.html',
                    {'form': form}
                )

        # Etapa 2: Validação e Criação Final
        elif step == 'wedding':
            form = WeddingForm(request.POST)
            client_data = request.session.get('new_wedding_client_data')

            if form.is_valid() and client_data:
                # Crie o cliente
                new_client = Client.objects.create(**client_data)

                # Crie o casamento e associe tudo
                wedding = form.save(commit=False)
                wedding.planner = planner
                wedding.client = new_client
                wedding.save()

                # Limpe a sessão e redirecione
                del request.session['new_wedding_client_data']
                response = HttpResponse()
                response['HX-Redirect'] = reverse('weddings:my_weddings')
                return response
            else:
                # Se algo der errado (form inválido ou sessão sumiu)
                return render(
                    request,
                    'weddings/partials/form-wedding.html',
                    {'form': form}
                )

    # Para o primeiro acesso (GET)
    client_form = ClientForm()
    return render(request, 'weddings/create-flow.html', {'form': client_form})


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


@login_required
def wedding_detail(request, id):
    planner = Planner.objects.get(user=request.user)
    wedding = get_object_or_404(Wedding, id=id, planner=planner)

    # Corrigido: filtra itens via budget__wedding
    itens = Item.objects.filter(budget__wedding=wedding)

    # Dados para aba orçamento (exemplo)
    orcamento_total = 85000
    gasto_atual = 52300
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
