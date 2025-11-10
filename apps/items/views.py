from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, ListView, UpdateView

from .forms import ItemForm
from .models import Item, Wedding


class PartialItemsView(LoginRequiredMixin, ListView):
    """Exibe a lista parcial de itens de um casamento específico."""
    model = Item
    template_name = "items/items_partial.html"
    context_object_name = "items"

    def get_queryset(self):
        # Filtra itens do casamento do usuário logado
        self.wedding = get_object_or_404(
            Wedding,
            id=self.kwargs["wedding_id"],
            planner=self.request.user
        )
        queryset = super().get_queryset()
        return queryset.filter(wedding=self.wedding).select_related("supplier")

    def get_context_data(self, **kwargs):
        # Adiciona o casamento ao contexto para o template
        context = super().get_context_data(**kwargs)
        context["wedding"] = self.wedding
        return context


class AddItemView(LoginRequiredMixin, CreateView):
    """Exibe e processa o formulário de adição de item."""
    model = Item
    form_class = ItemForm
    template_name = "items/partials/_item_form.html"

    def dispatch(self, request, *args, **kwargs):
        # Busca o casamento e o associa à view
        self.wedding = get_object_or_404(
            Wedding,
            id=self.kwargs["wedding_id"],
            planner=self.request.user
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # Inclui o casamento no contexto do template
        context = super().get_context_data(**kwargs)
        context["wedding"] = self.wedding
        return context

    def form_valid(self, form):
        # Salva o novo item e renderiza novamente a lista de itens
        item = form.save(commit=False)
        item.wedding = self.wedding
        item.save()
        items = Item.objects.filter(wedding=self.wedding).select_related("supplier")
        context = {"wedding": self.wedding, "items": items}
        return render(self.request, "items/items_partial.html", context)


class EditItemView(LoginRequiredMixin, UpdateView):
    """Permite editar um item existente."""
    model = Item
    form_class = ItemForm
    template_name = "items/partials/_item_form.html"

    def get_queryset(self):
        # Garante que o planner só edite itens dos seus casamentos
        return Item.objects.filter(wedding__planner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["wedding"] = self.object.wedding
        return context

    def form_valid(self, form):
        # Atualiza o item e recarrega a lista
        item = form.save()
        items = Item.objects.filter(wedding=item.wedding).select_related("supplier")
        context = {"wedding": item.wedding, "items": items}
        return render(self.request, "items/items_partial.html", context)


@require_POST
@login_required
def update_item_status(request, pk):
    """Atualiza o status de um item (Pendente, Em andamento ou Concluído)."""
    new_status = request.POST.get("status")
    valid_statuses = [status[0] for status in Item.STATUS_CHOICES]

    if new_status not in valid_statuses:
        return HttpResponseBadRequest("Status inválido")

    item = get_object_or_404(Item, pk=pk, wedding__planner=request.user)
    item.status = new_status
    item.save()

    items = Item.objects.filter(wedding=item.wedding).select_related("supplier")
    context = {"wedding": item.wedding, "items": items}
    return render(request, "items/items_partial.html", context)


@require_POST
@login_required
def delete_item(request, pk):
    """Exclui um item e recarrega a lista de itens."""
    item = get_object_or_404(Item, pk=pk, wedding__planner=request.user)
    wedding = item.wedding
    item.delete()

    items = Item.objects.filter(wedding=wedding).select_related("supplier")
    context = {"wedding": wedding, "items": items}
    return render(request, "items/items_partial.html", context)
