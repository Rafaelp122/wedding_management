from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.views.generic import CreateView, ListView

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
    template_name = "items/partials/add_item_form.html"

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
