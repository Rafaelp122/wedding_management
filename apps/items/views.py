from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, ListView, UpdateView

from .forms import ItemForm
from .models import Item, Wedding


class PartialItemsView(LoginRequiredMixin, ListView):
    """
    Exibe a lista parcial de itens para um casamento específico.
    """
    model = Item
    template_name = "items/items_partial.html"
    context_object_name = "items"

    def get_queryset(self):
        """
        Filtra os itens para pertencer apenas ao casamento especificado na URL
        e garante que o casamento pertença ao usuário logado.
        """
        # Primeiro, obtemos e validamos o casamento
        # Armazenamos 'self.wedding' para usá-lo em get_context_data
        self.wedding = get_object_or_404(
            Wedding,
            id=self.kwargs['wedding_id'],
            planner=self.request.user
        )

        # Filtra o queryset de Itens com base no casamento validado
        queryset = super().get_queryset()
        return queryset.filter(wedding=self.wedding).select_related("supplier")

    def get_context_data(self, **kwargs):
        """
        Adiciona o objeto 'wedding' ao contexto para que esteja disponível
        no template, assim como na FBV original.
        """
        context = super().get_context_data(**kwargs)
        # Adiciona o casamento (já buscado em get_queryset) ao contexto
        context['wedding'] = self.wedding
        return context


class AddItemView(LoginRequiredMixin, CreateView):
    """
    Exibe o formulário para adicionar um item (GET) e processa
    a adição do item (POST).
    """
    model = Item
    form_class = ItemForm
    template_name = "items/partials/_item_form.html"

    def dispatch(self, request, *args, **kwargs):
        """
        Busca e armazena o objeto 'wedding' antes que os métodos
        GET ou POST sejam executados.
        """
        # Valida e armazena o casamento em 'self' para ser usado
        # em get_context_data e form_valid
        self.wedding = get_object_or_404(
            Wedding,
            id=self.kwargs['wedding_id'],
            planner=self.request.user
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Adiciona o objeto 'wedding' ao contexto do template do formulário.
        """
        context = super().get_context_data(**kwargs)
        context['wedding'] = self.wedding
        return context

    def form_valid(self, form):
        """
        Chamado quando o formulário é válido (POST).
        Associa o item ao casamento antes de salvar.
        """
        # 'commit=False' nos permite modificar o objeto antes de salvar
        item = form.save(commit=False)
        item.wedding = self.wedding  # Associa o item ao casamento correto
        item.save()

        items = Item.objects.filter(
            wedding=self.wedding
        ).select_related("supplier")
        context = {
            "wedding": self.wedding,
            "items": items
        }
        return render(self.request, "items/items_partial.html", context)


class EditItemView(LoginRequiredMixin, UpdateView):
    model = Item
    form_class = ItemForm
    # Usa o mesmo template de formulário que a AddItemView
    template_name = "items/partials/_item_form.html"

    def get_queryset(self):
        # Garante que o usuário só pode editar seus próprios itens
        return Item.objects.filter(wedding__planner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Passa 'wedding' para o template (para o botão 'Cancelar')
        context['wedding'] = self.object.wedding
        return context

    def form_valid(self, form):
        item = form.save()
        items = Item.objects.filter(
            wedding=item.wedding
        ).select_related("supplier")

        context = {
            "wedding": item.wedding,
            "items": items
        }
        return render(self.request, "items/items_partial.html", context)


@require_POST
@login_required
def update_item_status(request, pk):
    new_status = request.POST.get('status')
    valid_statuses = [status[0] for status in Item.STATUS_CHOICES]
    if new_status not in valid_statuses:
        return HttpResponseBadRequest("Status inválido")

    item = get_object_or_404(Item, pk=pk, wedding__planner=request.user)

    item.status = new_status
    item.save()

    items = Item.objects.filter(
        wedding=item.wedding
    ).select_related("supplier")
    context = {
        "wedding": item.wedding,
        "items": items
    }
    return render(request, "items/items_partial.html", context)


@require_POST
@login_required
def delete_item(request, pk):
    item = get_object_or_404(Item, pk=pk, wedding__planner=request.user)
    wedding = item.wedding

    item.delete()

    items = Item.objects.filter(
        wedding=wedding
    ).select_related("supplier")
    context = {
        "wedding": wedding,
        "items": items
    }
    return render(request, "items/items_partial.html", context)
