from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
    View,
    TemplateView,
)

import logging
from .mixins import (
    PlannerOwnershipMixin,  # Apenas Segurança
    WeddingFormLayoutMixin,  # Apenas Layout de Formulário
    WeddingListActionsMixin,  # O "Pacote de Lista" (Query, Pag, HTMX)
)
from .models import Wedding

logger = logging.getLogger(__name__)


class WeddingListView(
    PlannerOwnershipMixin,  # Segurança (para garantir que a pág. carregue)
    WeddingListActionsMixin,  # Lógica de Lista (Query, Paginação, Contexto)
    TemplateView,
):
    """
    Renderiza a página completa (F5) ou o partial da lista (HTMX).
    Usar TemplateView é mais simples, pois o
    WeddingListActionsMixin já faz todo o trabalho.
    """

    template_name = "weddings/list.html"

    def get_context_data(self, **kwargs):
        """
        Constrói o contexto para o carregamento da página inteira (F5).

        Ele usa o mixin 'build_paginated_context' para obter os dados
        da lista e adiciona metadados de paginação para o template.
        """
        context = super().get_context_data(**kwargs)

        # Pega os parâmetros do GET (q, sort, page)
        request_params = self.request.GET.copy()

        logger.debug(
            f"Construindo contexto de lista para F5 load. Params: {request_params}"
        )

        # herda build_paginated_context de "WeddingPaginationContextMixin"
        list_context = self.build_paginated_context(request_params)

        context.update(list_context)

        context["pagination_url_name"] = "weddings:my_weddings"
        context["pagination_target"] = "#wedding-list-container"
        context["pagination_aria_label"] = "Paginação de Casamentos"
        return context

    def render_to_response(self, context, **response_kwargs):
        """
        Decide qual template renderizar (página inteira vs. partial).

        Este é o "ponto de entrada" para requisições GET do HTMX
        (paginação, busca, filtro), renderizando apenas o partial.
        """
        # Lida com as requisições HTMX (filtro, busca, paginação)
        if self.request.htmx:
            logger.debug("Requisição HTMX (GET) recebida, renderizando partial.")
            # Renderiza o partial
            return render(
                self.request, "weddings/partials/_list_and_pagination.html", context
            )

        # Se for um F5, renderiza a página inteira
        return super().render_to_response(context, **response_kwargs)


class WeddingCreateView(
    PlannerOwnershipMixin,  # Segurança
    WeddingListActionsMixin,  # Resposta HTMX da Lista
    WeddingFormLayoutMixin,  # Layout do Formulário
    CreateView,
):
    """
    Lida com a criação de um novo Casamento.
    Responde com o formulário (GET) ou a lista atualizada (POST).
    """
    model = Wedding
    # form_class e template_name vêm do WeddingFormLayoutMixin

    def get_context_data(self, **kwargs):
        """
        Adiciona o contexto dinâmico do modal (título, botão, URL).
        """
        context = super().get_context_data(**kwargs)
        context["modal_title"] = "Novo Casamento"
        context["submit_button_text"] = "Salvar Casamento"
        context["hx_post_url"] = reverse("weddings:create_wedding")
        return context

    def form_valid(self, form):
        """
        Define o 'planner' do casamento como o usuário logado e
        retorna a lista de casamentos atualizada via HTMX.
        """
        form.instance.planner = self.request.user
        form.save()
        logger.info(
            f"Novo casamento criado: '{form.instance}' (ID: {form.instance.id})"
            f"pelo usuário {self.request.user.id}"
        )
        # render_wedding_list_response vem do WeddingListActionsMixin
        return self.render_wedding_list_response()

    def form_invalid(self, form):
        """Loga falhas de validação do formulário."""
        logger.warning(
            f"Tentativa de criação de casamento falhou (inválido): {form.errors}"
        )
        return super().form_invalid(form)


class WeddingUpdateView(
    PlannerOwnershipMixin,  # Segurança (usa get_queryset)
    WeddingListActionsMixin,  # Resposta HTMX da Lista
    WeddingFormLayoutMixin,  # Layout do Formulário
    UpdateView,
):
    """
    Lida com a atualização de um Casamento.
    Responde com o formulário pré-preenchido (GET) ou a lista atualizada (POST).
    """
    model = Wedding
    pk_url_kwarg = "id"
    # form_class e template_name vêm do WeddingFormLayoutMixin
    # get_queryset (segurança) vem do PlannerOwnershipMixin

    def get_context_data(self, **kwargs):
        """
        Adiciona o contexto dinâmico do modal (título, botão, URL de post).
        """
        context = super().get_context_data(**kwargs)
        context["modal_title"] = "Editar Casamento"
        context["submit_button_text"] = "Salvar Alterações"
        context["hx_post_url"] = reverse(
            "weddings:edit_wedding", kwargs={"id": self.object.pk}
        )
        return context

    def form_valid(self, form):
        """
        Salva as alterações e retorna a lista de casamentos
        atualizada via HTMX.
        """
        form.save()
        logger.info(f"Casamento {self.object.id} atualizado pelo usuário {self.request.user.id}")
        # render_wedding_list_response vem do WeddingListActionsMixin
        return self.render_wedding_list_response()

    def form_invalid(self, form):
        """Loga falhas de validação do formulário."""
        logger.warning(
            f"Tentativa de atualização do casamento {self.object.id} falhou (inválido): {form.errors}"
        )
        return super().form_invalid(form)


class WeddingDeleteView(
    PlannerOwnershipMixin,  # Segurança (usa get_queryset)
    WeddingListActionsMixin,  # Resposta HTMX da Lista
    DeleteView,
):
    """
    Lida com a exclusão de um Casamento.
    Responde com o modal de confirmação (GET) ou a lista atualizada (POST).
    """
    model = Wedding
    template_name = "partials/confirm_delete_modal.html"
    pk_url_kwarg = "id"
    # get_queryset (segurança) vem do PlannerOwnershipMixin

    def get_context_data(self, **kwargs):
        """Adiciona contexto para o modal de confirmação."""
        context = super().get_context_data(**kwargs)
        context["object_name"] = str(self.object)
        context["object_type"] = "o casamento"
        context["hx_post_url"] = reverse(
            "weddings:delete_wedding", kwargs={"id": self.object.pk}
        )
        context["hx_target_id"] = "#wedding-list-container"
        return context

    def post(self, request, *args, **kwargs):
        """
        Deleta o objeto e retorna a lista de casamentos
        atualizada via HTMX (em vez do redirect padrão).
        """
        self.object = self.get_object()
        object_repr = str(self.object)
        self.object.delete()

        logger.info(
            f"Casamento DELETADO: '{object_repr}' (ID: {self.kwargs['id']}) "
            f"pelo usuário {self.request.user.id}"
        )
        # render_wedding_list_response vem do WeddingListActionsMixin
        return self.render_wedding_list_response()


class UpdateWeddingStatusView(
    PlannerOwnershipMixin,  # Segurança (usa get_queryset)
    WeddingListActionsMixin,  # Resposta HTMX da Lista
    View,
):
    """
    View 'apenas-POST' para atualizar o status de um Casamento.
    (Ex: de "Em Andamento" para "Concluído").
    """
    model = Wedding  # Informa ao PlannerOwnershipMixin qual model usar
    # get_queryset (segurança) vem do PlannerOwnershipMixin

    def post(self, request, *args, **kwargs):
        """
        Valida e atualiza o status do casamento, depois
        retorna a lista de casamentos atualizada via HTMX.
        """
        try:
            wedding = self.get_queryset().get(pk=self.kwargs["id"])
        except Wedding.DoesNotExist:
            logger.warning(
                f"Tentativa de mudança de status falhou (Não Encontrado ou Sem Permissão). "
                f"Casamento ID: {self.kwargs['id']}, Usuário: {self.request.user.id}"
            )
            return HttpResponseBadRequest("Casamento não encontrado ou sem permissão.")

        new_status = request.POST.get("status")
        valid_statuses = [status[0] for status in Wedding.STATUS_CHOICES]

        if new_status not in valid_statuses:
            logger.warning(
                f"Tentativa de mudança de status falhou (Status Inválido): '{new_status}'"
            )
            return HttpResponseBadRequest("Status inválido ou Model não atualizado.")

        old_status = wedding.status
        wedding.status = new_status
        wedding.save()

        logger.info(
            f"Status do casamento {wedding.id} alterado de '{old_status}' "
            f"para '{new_status}' pelo usuário {self.request.user.id}"
        )

        # render_wedding_list_response vem do WeddingListActionsMixin
        return self.render_wedding_list_response(trigger="listUpdated")


class WeddingDetailView(PlannerOwnershipMixin, DetailView):  # APENAS Segurança
    """
    SignatureView (View de Assinatura): Apenas exibe os detalhes.

    Herda apenas o mixin de segurança, pois não precisa de
    lógica de formulário ou de lista.
    """
    model = Wedding
    template_name = "weddings/detail.html"
    context_object_name = "wedding"
    pk_url_kwarg = "wedding_id"
