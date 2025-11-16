from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    UpdateView,
    View,
    TemplateView,  # Usaremos TemplateView para a lista
)
from .models import Item
from .mixins import (
    ItemWeddingContextMixin,  # OBRIGATÓRIO: Carrega 'self.wedding'
    ItemPlannerSecurityMixin,  # Segurança para Update/Delete
    ItemFormLayoutMixin,  # Layout do Formulário
    ItemListActionsMixin,  # O "Pacote de Lista" (Query, Pag, HTMX)
)


class ItemListView(
    ItemWeddingContextMixin,  # Carrega self.wedding
    ItemListActionsMixin,  # Fornece get_base_queryset, build_paginated_context
    TemplateView,
):
    """
    Exibe a aba de itens completa ou apenas o partial da lista.
    """

    template_name = "items/item_list.html"  # A "aba" inteira

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 'build_paginated_context' vem do ItemListActionsMixin
        # e usa 'self.wedding' do ItemWeddingContextMixin
        context.update(self.build_paginated_context(self.request.GET))

        context["pagination_url_name"] = "items:partial_items"
        # O 'pagination_target' é o ID do container da lista
        context["pagination_target"] = "#item-list-container"
        # Acessibilidade
        context["pagination_aria_label"] = "Paginação de Itens"
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.htmx:
            htmx_target = self.request.headers.get("HX-Target")

            # Se o target for o container INTERNO (filtro, paginação)...
            if htmx_target == "item-list-container":
                # Renderiza SÓ o partial
                return render(
                    self.request, "items/partials/_list_and_pagination.html", context
                )

            # Se o target for '#tab-items' (clique na aba),
            # o 'if' falha e renderiza a aba inteira abaixo.

        # Retorna a ABA INTEIRA (para F5 ou clique inicial na aba)
        return super().render_to_response(context, **response_kwargs)


class AddItemView(
    ItemWeddingContextMixin,  # Carrega self.wedding (de wedding_id)
    ItemFormLayoutMixin,  # Layout do formulário
    ItemListActionsMixin,  # Para render_item_list_response
    CreateView,
):
    """Exibe e processa o formulário de adição de item."""

    model = Item  # Necessário para CreateView

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["modal_title"] = "Adicionar Novo Item"
        context["submit_button_text"] = "Salvar Item"
        context["hx_post_url"] = reverse(
            "items:add_item", kwargs={"wedding_id": self.wedding.id}
        )
        return context

    def form_valid(self, form):
        item = form.save(commit=False)
        item.wedding = self.wedding
        item.save()
        # 'render_item_list_response' vem do ItemListActionsMixin
        return self.render_item_list_response(trigger="listUpdated")


class EditItemView(
    ItemWeddingContextMixin,  # Carrega self.wedding (de pk)
    ItemPlannerSecurityMixin,  # Fornece get_queryset()
    ItemFormLayoutMixin,  # Layout do formulário
    ItemListActionsMixin,  # Para render_item_list_response
    UpdateView,
):
    """Permite editar um item existente."""

    model = Item  # Necessário para UpdateView
    pk_url_kwarg = "pk"
    # get_queryset() vem do ItemPlannerSecurityMixin

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["modal_title"] = "Editar Item"
        context["submit_button_text"] = "Salvar Alterações"
        context["hx_post_url"] = reverse(
            "items:edit_item", kwargs={"pk": self.object.pk}
        )
        return context

    def form_valid(self, form):
        form.save()
        return self.render_item_list_response(trigger="listUpdated")


class UpdateItemStatusView(
    ItemWeddingContextMixin,  # Carrega self.wedding (de pk)
    ItemPlannerSecurityMixin,  # Fornece get_queryset()
    ItemListActionsMixin,  # Para render_item_list_response
    View,
):
    """Atualiza o status de um item."""

    model = Item  # Informa ao ItemPlannerSecurityMixin qual model usar

    def post(self, request, *args, **kwargs):
        try:
            # get_queryset() vem do ItemPlannerSecurityMixin
            item = self.get_queryset().get(pk=self.kwargs["pk"])
        except self.model.DoesNotExist:
            return HttpResponseBadRequest("Item não encontrado ou sem permissão.")

        new_status = request.POST.get("status")
        valid_statuses = [status[0] for status in self.model.STATUS_CHOICES]

        if new_status not in valid_statuses:
            return HttpResponseBadRequest("Status inválido")

        item.status = new_status
        item.save()
        return self.render_item_list_response(trigger="listUpdated")


class ItemDeleteView(
    ItemWeddingContextMixin,  # Carrega self.wedding (de pk)
    ItemPlannerSecurityMixin,  # Fornece get_queryset()
    ItemListActionsMixin,  # Para render_item_list_response
    DeleteView,
):
    """Exclui um item."""

    model = Item  # Necessário para DeleteView
    pk_url_kwarg = "pk"
    template_name = "partials/confirm_delete_modal.html"
    # get_queryset() vem do ItemPlannerSecurityMixin

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_name"] = str(self.object)
        context["object_type"] = "o item"
        context["hx_post_url"] = reverse(
            "items:delete_item", kwargs={"pk": self.object.pk}
        )
        context["hx_target_id"] = "#item-list-container"
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return self.render_item_list_response(trigger="listUpdated")
