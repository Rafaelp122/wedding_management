import logging

from django.contrib import messages
from django.http import (
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseNotFound,
)
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    TemplateView,
    UpdateView,
    View,
)

from .constants import (
    WEDDING_LIST_CONTAINER_ID,
    WEDDING_LIST_URL_NAME,
    WEDDING_PAGINATION_ARIA_LABEL,
)
from .mixins import (
    PlannerOwnershipMixin,  # Apenas Segurança
    WeddingFormLayoutMixin,  # Apenas Layout de Formulário
    WeddingListActionsMixin,  # O "Pacote de Lista" (Query, Pag, HTMX)
    WeddingModalContextMixin,  # Contexto de Modais
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
    pagination_url_name = WEDDING_LIST_URL_NAME
    pagination_target = WEDDING_LIST_CONTAINER_ID
    pagination_aria_label = WEDDING_PAGINATION_ARIA_LABEL

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
            f"Construindo contexto de lista para F5 load. "
            f"Params: {request_params}"
        )

        # herda build_paginated_context de "WeddingPaginationContextMixin"
        list_context = self.build_paginated_context(request_params)

        context.update(list_context)

        context["pagination_url_name"] = self.pagination_url_name
        context["pagination_target"] = self.pagination_target
        context["pagination_aria_label"] = self.pagination_aria_label
        return context

    def render_to_response(self, context, **response_kwargs):
        """
        Decide qual template renderizar (página inteira vs. partial).

        Este é o "ponto de entrada" para requisições GET do HTMX
        (paginação, busca, filtro), renderizando apenas o partial.
        """
        # Lida com as requisições HTMX (filtro, busca, paginação)
        if self.request.htmx:
            logger.debug(
                "Requisição HTMX (GET) recebida, renderizando partial."
            )
            # Renderiza o partial
            return render(
                self.request,
                "weddings/partials/_list_and_pagination.html",
                context
            )

        # Se for um F5, renderiza a página inteira
        return super().render_to_response(context, **response_kwargs)


class WeddingCreateView(
    PlannerOwnershipMixin,  # Segurança
    WeddingListActionsMixin,  # Resposta HTMX da Lista
    WeddingModalContextMixin,  # Contexto do Modal
    WeddingFormLayoutMixin,  # Layout do Formulário
    CreateView,
):
    """
    Lida com a criação de um novo Casamento.
    Responde com o formulário (GET) ou a lista atualizada (POST).
    """

    model = Wedding
    modal_title = "Novo Casamento"
    submit_button_text = "Salvar Casamento"

    def get_hx_post_url(self) -> str:
        """Retorna a URL para o POST do formulário."""
        return reverse("weddings:create_wedding")

    def form_valid(self, form):
        """
        Define o 'planner' do casamento como o usuário logado e
        retorna a lista de casamentos atualizada via HTMX.
        """
        form.instance.planner = self.request.user
        form.save()
        logger.info(
            f"Novo casamento criado: '{form.instance}' "
            f"(ID: {form.instance.id}) "
            f"pelo usuário {self.request.user.id}"
        )
        # render_wedding_list_response vem do WeddingListActionsMixin
        return self.render_wedding_list_response()

    def form_invalid(self, form):
        """Loga falhas de validação do formulário."""
        # Log apenas erros não-field (inesperados)
        if form.non_field_errors():
            logger.warning(
                f"Erro inesperado na criação de casamento: "
                f"{form.non_field_errors()}"
            )
        return super().form_invalid(form)


class WeddingUpdateView(
    PlannerOwnershipMixin,  # Segurança (usa get_queryset)
    WeddingListActionsMixin,  # Resposta HTMX da Lista
    WeddingModalContextMixin,  # Contexto do Modal
    WeddingFormLayoutMixin,  # Layout do Formulário
    UpdateView,
):
    """
    Lida com a atualização de um Casamento.
    Responde com o formulário pré-preenchido (GET) ou a lista
    atualizada (POST).
    """

    model = Wedding
    pk_url_kwarg = "id"
    modal_title = "Editar Casamento"
    submit_button_text = "Salvar Alterações"

    def get_hx_post_url(self) -> str:
        """Retorna a URL para o POST do formulário."""
        return reverse(
            "weddings:edit_wedding", kwargs={"id": self.object.pk}
        )

    def form_valid(self, form):
        """
        Salva as alterações e retorna a lista de casamentos
        atualizada via HTMX.
        """
        form.save()
        logger.info(
            f"Casamento {self.object.id} atualizado "
            f"pelo usuário {self.request.user.id}"
        )
        # render_wedding_list_response vem do WeddingListActionsMixin
        return self.render_wedding_list_response()

    def form_invalid(self, form):
        """Loga falhas de validação do formulário."""
        # Log apenas erros não-field (inesperados)
        if form.non_field_errors():
            logger.warning(
                f"Erro inesperado na atualização do casamento "
                f"{self.object.id}: {form.non_field_errors()}"
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

    def post(self, request, *args, **kwargs):
        """
        Valida e atualiza o status do casamento, depois
        retorna a lista de casamentos atualizada via HTMX.
        """
        wedding_id = self.kwargs["id"]

        # Verifica se o casamento existe
        try:
            wedding = Wedding.objects.get(pk=wedding_id)
        except Wedding.DoesNotExist:
            logger.warning(
                f"Tentativa de acesso a casamento inexistente. "
                f"ID: {wedding_id}, Usuário: {request.user.id}"
            )
            messages.error(request, "Casamento não encontrado.")
            return HttpResponseNotFound(
                "Casamento não encontrado.",
                content_type="text/html"
            )

        # Verifica ownership explicitamente
        if wedding.planner != request.user:
            logger.warning(
                f"Tentativa de acesso não autorizado. "
                f"Casamento ID: {wedding_id}, "
                f"Usuário: {request.user.id}"
            )
            messages.error(
                request, "Você não tem permissão para este recurso."
            )
            return HttpResponseForbidden(
                "Sem permissão.",
                content_type="text/html"
            )

        new_status = request.POST.get("status")

        # Valida se o status é válido usando TextChoices
        try:
            Wedding.StatusChoices(new_status)
        except ValueError:
            logger.warning(f"Status inválido recebido: '{new_status}'")
            messages.error(request, f"Status '{new_status}' não é válido.")
            return HttpResponseBadRequest(
                "Status inválido ou Model não atualizado."
            )

        old_status = wedding.status
        wedding.status = new_status
        wedding.save()

        logger.info(
            f"Status do casamento {wedding.id} alterado de "
            f"'{old_status}' para '{new_status}' "
            f"pelo usuário {request.user.id}"
        )

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
