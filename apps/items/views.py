from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, ListView, UpdateView, View

from .mixins import ItemBaseMixin, ItemFormLayoutMixin


class ItemListView(ItemBaseMixin, ListView):
    """
    Exibe a lista parcial de itens (com paginação, filtro e busca).
    Lida com a carga inicial da aba E com
    as requisições HTMX de filtro/busca/paginação.
    """
    template_name = "items/items_list.html"

    def get_queryset(self):
        # O Mixin 'dispatch' já nos deu 'self.wedding'
        sort = self.request.GET.get('sort', 'id')
        q = self.request.GET.get('q', None)
        category = self.request.GET.get('category', None)

        # Chama o 'get_base_queryset' com todos os filtros
        return self.get_base_queryset(sort=sort, q=q, category=category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Constrói o contexto paginado completo
        context.update(
            self.build_paginated_context(self.request.GET)
        )
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.htmx:
            htmx_target = self.request.headers.get('HX-Target')

            if htmx_target == 'item-list-container':
                # Retorna SÓ a lista (para Filtro/Busca/Paginação)
                return render(
                    self.request, 
                    "items/partials/_list_and_pagination.html", 
                    context
                )

        # Retorna a ABA INTEIRA (para o clique na aba)
        return super().render_to_response(context, **response_kwargs)


class AddItemView(ItemBaseMixin, ItemFormLayoutMixin, CreateView):
    """Exibe e processa o formulário de adição de item."""
    # dispatch, get_queryset, get_context_data, get_form_kwargs
    # form_class, e template_name já vêm dos Mixins!

    def form_valid(self, form):
        item = form.save(commit=False)
        item.wedding = self.wedding  # 'self.wedding' vem do dispatch do Mixin
        item.save()
        # Retorna a resposta HTMX completa
        return self.render_item_list_response(trigger="listUpdated")


class EditItemView(ItemBaseMixin, ItemFormLayoutMixin, UpdateView):
    """Permite editar um item existente."""
    # dispatch, get_queryset (segurança), get_context_data, get_form_kwargs
    # form_class, e template_name já vêm dos Mixins!

    def form_valid(self, form):
        form.save()
        # Retorna a resposta HTMX completa
        return self.render_item_list_response(trigger="listUpdated")


class UpdateItemStatusView(ItemBaseMixin, View):
    """Atualiza o status de um item."""

    def post(self, request, *args, **kwargs):
        try:
            # self.get_queryset() vem do mixin e já filtra por planner
            item = self.get_queryset().get(pk=self.kwargs['pk'])
        except self.model.DoesNotExist:
            return HttpResponseBadRequest(
                "Item não encontrado ou sem permissão."
            )

        new_status = request.POST.get("status")

        valid_statuses = [status[0] for status in self.model.STATUS_CHOICES]

        if new_status not in valid_statuses:
            return HttpResponseBadRequest("Status inválido")

        item.status = new_status
        item.save()

        # Retorna a lista completa (com paginação/filtros preservados)
        return self.render_item_list_response(trigger="listUpdated")


class ItemDeleteView(ItemBaseMixin, DeleteView):
    """Exclui um item."""
    template_name = "partials/confirm_delete_modal.html"  # Modal reutilizável

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_name'] = str(self.object)
        context['object_type'] = 'o item'
        context['hx_post_url'] = reverse(
            'items:delete_item', kwargs={'pk': self.object.pk}
        )
        context['hx_target_id'] = '#items-wrapper'  # Container dos Itens
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        # Retorna a resposta HTMX completa
        return self.render_item_list_response(trigger="listUpdated")
