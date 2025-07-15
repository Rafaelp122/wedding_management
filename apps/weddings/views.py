from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.users.models import Planner

from .forms import WeddingForm
from .models import Wedding

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
    weddings = Wedding.objects.filter(planner=planner).prefetch_related("clients")

    weddings_with_clients = []
    for idx, w in enumerate(weddings):
        clients = list(w.clients.all())
        first = clients[0] if clients else None
        last = clients[-1] if clients else None
        gradient = GRADIENTS[
            idx % len(GRADIENTS)
        ]  # escolhe uma cor da lista de forma cíclica
        weddings_with_clients.append(
            {
                "wedding": w,
                "first_client": first,
                "last_client": last,
                "gradient": gradient,
            }
        )

    return render(
        request, "weddings/list.html", {"weddings_with_clients": weddings_with_clients}
    )


@login_required
def create_wedding(request):
    planner = Planner.objects.get(user=request.user)
    if request.method == "POST":
        form = WeddingForm(request.POST)
        if form.is_valid():
            wedding = form.save(commit=False)
            wedding.planner = planner
            wedding.save()
            form.save_m2m()
            return redirect("weddings:my_weddings")
    else:
        form = WeddingForm()
    return render(request, "weddings/create.html", {"form": form})


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

    return render(request, "weddings/create.html", {"form": form, "wedding": wedding})


@login_required
@require_POST
def delete_wedding(request, id):
    planner = Planner.objects.get(user=request.user)
    wedding = get_object_or_404(Wedding, id=id, planner=planner)
    wedding.delete()
    return redirect("weddings:my_weddings")
