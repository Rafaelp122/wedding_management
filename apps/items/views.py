import logging

from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    TemplateView,  # Usaremos TemplateView para a lista
    UpdateView,
    View,
)

from apps.contracts.models import Contract

from .mixins import (
    ItemFormLayoutMixin,  # Layout do Formulário
    ItemListActionsMixin,  # O "Pacote de Lista" (Query, Pag, HTMX)
    ItemPlannerSecurityMixin,  # Segurança para Update/Delete
    ItemWeddingContextMixin,  # OBRIGATÓRIO: Carrega 'self.wedding'
)
from .models import Item

logger = logging.getLogger(__name__)


class ItemListView(
    ItemWeddingContextMixin,  # Carrega self.wedding
    ItemListActionsMixin,  # Fornece get_base_queryset, build_paginated_context
    TemplateView,
):
    """
    Exibe a aba de itens completa (F5 / clique na aba)
    ou apenas o partial da lista (filtro / paginação).
    """

    template_name = "items/item_list.html"  # A "aba" inteira

    def get_context_data(self, **kwargs):
        """
        Constrói o contexto para a 'aba' de itens.

        Este método é chamado em um F5 ou no primeiro clique na aba.
        Ele usa o mixin 'build_paginated_context' para obter os dados
        da lista.
        """
        context = super().get_context_data(**kwargs)
        logger.debug(
            f"Construindo contexto da aba de itens para o casamento {self.wedding.id}"
        )
        # 'build_paginated_context' vem do ItemListActionsMixin
        # e usa 'self.wedding' do ItemWeddingContextMixin
        context.update(self.build_paginated_context(self.request.GET))

        context["pagination_url_name"] = "items:partial_items"
        context["pagination_target"] = "#item-list-container"
        context["pagination_aria_label"] = "Paginação de Itens"
        return context

    def render_to_response(self, context, **response_kwargs):
        """
        Renderiza a aba inteira (F5) ou o partial (filtro/paginação).

        Diferencia uma requisição HTMX para a aba inteira (target na aba)
        de uma requisição para o container da lista (target no container).
        """
        if self.request.htmx:
            htmx_target = self.request.headers.get("HX-Target")

            # Se o target for o container INTERNO (filtro, paginação)...
            if htmx_target == "item-list-container":
                logger.debug(
                    "Requisição HTMX (GET) recebida, renderizando partial de lista."
                )
                # Renderiza SÓ o partial
                return render(
                    self.request, "items/partials/_list_and_pagination.html", context
                )
            logger.debug("Requisição HTMX (GET) recebida, renderizando aba inteira.")

        # Retorna a ABA INTEIRA (para F5 ou clique inicial na aba)
        return super().render_to_response(context, **response_kwargs)


class AddItemView(
    ItemWeddingContextMixin,  # Carrega self.wedding (de wedding_id)
    ItemFormLayoutMixin,  # Layout do formulário
    ItemListActionsMixin,  # Para render_item_list_response
    CreateView,
):
    """
    Exibe (GET) e processa (POST) o formulário de adição de item.
    """

    model = Item  # Necessário para CreateView

    def get_context_data(self, **kwargs):
        """Adiciona o contexto dinâmico do modal (título, botão, URL)."""
        context = super().get_context_data(**kwargs)
        context["modal_title"] = "Adicionar Novo Item"
        context["submit_button_text"] = "Salvar Item"
        context["hx_post_url"] = reverse(
            "items:add_item", kwargs={"wedding_id": self.wedding.id}
        )
        return context

    def form_valid(self, form):
        """
        Define o 'wedding', salva o item e cria o contrato associado,
        depois retorna a lista de itens atualizada.
        """
        item = form.save(commit=False)
        item.wedding = self.wedding
        item.save()
        # Cria o contrato associado ao item recém-criado
        Contract.objects.create(item=item)

        logger.info(
            f"Novo item '{item}' (ID: {item.id}) e contrato associado "
            f"criados para o casamento {self.wedding.id} pelo usuário {self.request.user.id}"
        )
        # 'render_item_list_response' vem do ItemListActionsMixin
        return self.render_item_list_response(trigger="listUpdated")

    def form_invalid(self, form):
        """Loga falhas de validação do formulário."""
        logger.warning(
            f"Tentativa de criação de item falhou (inválido) "
            f"para o casamento {self.wedding.id}: {form.errors}"
        )
        return super().form_invalid(form)


class EditItemView(
    ItemWeddingContextMixin,  # Carrega self.wedding (de pk)
    ItemPlannerSecurityMixin,  # Fornece get_queryset()
    ItemFormLayoutMixin,  # Layout do formulário
    ItemListActionsMixin,  # Para render_item_list_response
    UpdateView,
):
    """Exibe (GET) e processa (POST) o formulário de edição de item."""

    model = Item  # Necessário para UpdateView
    pk_url_kwarg = "pk"
    # get_queryset() vem do ItemPlannerSecurityMixin

    def get_context_data(self, **kwargs):
        """Adiciona o contexto dinâmico do modal (título, botão, URL de post)."""
        context = super().get_context_data(**kwargs)
        context["modal_title"] = "Editar Item"
        context["submit_button_text"] = "Salvar Alterações"
        context["hx_post_url"] = reverse(
            "items:edit_item", kwargs={"pk": self.object.pk}
        )
        return context

    def form_valid(self, form):
        """Salva as alterações e retorna a lista de itens atualizada."""
        item = form.save()
        logger.info(
            f"Item {item.id} ('{item.name}') atualizado "
            f"pelo usuário {self.request.user.id}"
        )
        return self.render_item_list_response(trigger="listUpdated")

    def form_invalid(self, form):
        """Loga falhas de validação do formulário."""
        logger.warning(
            f"Tentativa de atualização do item {self.object.id} falhou (inválido): {form.errors}"
        )
        return super().form_invalid(form)


class UpdateItemStatusView(
    ItemWeddingContextMixin,  # Carrega self.wedding (de pk)
    ItemPlannerSecurityMixin,  # Fornece get_queryset()
    ItemListActionsMixin,  # Para render_item_list_response
    View,
):
    """View 'apenas-POST' para atualizar o status de um item (Ex: Concluído)."""

    model = Item  # Informa ao ItemPlannerSecurityMixin qual model usar

    def post(self, request, *args, **kwargs):
        """Valida e atualiza o status do item."""
        try:
            # get_queryset() vem do ItemPlannerSecurityMixin (segurança)
            item = self.get_queryset().get(pk=self.kwargs["pk"])
        except self.model.DoesNotExist:
            # A segurança do dispatch já deve ter pego isso, mas é uma
            # boa prática ter uma verificação dupla.
            logger.warning(
                f"Tentativa de mudança de status falhou (Não Encontrado ou Sem Permissão). "
                f"Item ID: {self.kwargs['pk']}, Usuário: {self.request.user.id}"
            )
            return HttpResponseBadRequest("Item não encontrado ou sem permissão.")

        new_status = request.POST.get("status")
        valid_statuses = [status[0] for status in self.model.STATUS_CHOICES]

        if new_status not in valid_statuses:
            logger.warning(
                f"Tentativa de mudança de status falhou (Status Inválido): '{new_status}' "
                f"para o item {item.id}"
            )
            return HttpResponseBadRequest("Status inválido")

        old_status = item.status
        item.status = new_status
        item.save()
        logger.info(
            f"Status do item {item.id} ('{item.name}') alterado de '{old_status}' "
            f"para '{new_status}' pelo usuário {self.request.user.id}"
        )
        return self.render_item_list_response(trigger="listUpdated")


class ItemDeleteView(
    ItemWeddingContextMixin,  # Carrega self.wedding (de pk)
    ItemPlannerSecurityMixin,  # Fornece get_queryset()
    ItemListActionsMixin,  # Para render_item_list_response
    DeleteView,
):
    """Exibe (GET) o modal de confirmação e processa (POST) a exclusão."""

    model = Item  # Necessário para DeleteView
    pk_url_kwarg = "pk"
    template_name = "partials/confirm_delete_modal.html"
    # get_queryset() vem do ItemPlannerSecurityMixin

    def get_context_data(self, **kwargs):
        """Adiciona contexto para o modal de confirmação."""
        context = super().get_context_data(**kwargs)
        context["object_name"] = str(self.object)
        context["object_type"] = "o item"
        context["hx_post_url"] = reverse(
            "items:delete_item", kwargs={"pk": self.object.pk}
        )
        context["hx_target_id"] = "#item-list-container"
        return context

    def post(self, request, *args, **kwargs):
        """Deleta o objeto e retorna a lista de itens atualizada."""
        self.object = self.get_object()
        # Captura a representação do objeto ANTES de deletar
        object_repr = str(self.object)
        self.object.delete()

        logger.info(
            f"Item DELETADO: '{object_repr}' (ID: {self.kwargs['pk']}) "
            f"pelo usuário {self.request.user.id}"
        )
        return self.render_item_list_response(trigger="listUpdated")
