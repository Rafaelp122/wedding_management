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

from .mixins import (
    PlannerOwnershipMixin,     # Apenas Segurança
    WeddingFormLayoutMixin,    # Apenas Layout de Formulário
    WeddingListActionsMixin,   # O "Pacote de Lista" (Query, Pag, HTMX)
)
from .models import Wedding


class WeddingListView(
    PlannerOwnershipMixin,      # Segurança (para garantir que a pág. carregue)
    WeddingListActionsMixin,  # Lógica de Lista (Query, Paginação, Contexto)
    TemplateView              # MAIS LIMPO que ListView
):
    """
    Renderiza a página completa (F5) ou o partial da lista (HTMX).
    Usar TemplateView é mais simples, pois nosso
    WeddingListActionsMixin JÁ faz todo o trabalho.
    """
    template_name = "weddings/list.html"  # A página COMPLETA

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Pega os parâmetros do GET (q, sort, page)
        request_params = self.request.GET.copy()

        # build_paginated_context (do mixin) faz TUDO:
        list_context = self.build_paginated_context(request_params)

        context.update(list_context)
        return context

    def render_to_response(self, context, **response_kwargs):
        # Lida com as requisições HTMX (filtro, busca, paginação)
        if self.request.htmx:
            # Renderiza o partial
            return render(
                self.request,
                "weddings/partials/_list_and_pagination.html",
                context
            )

        # Se for um F5, renderiza a página inteira
        return super().render_to_response(context, **response_kwargs)


class WeddingCreateView(
    PlannerOwnershipMixin,     # Segurança
    WeddingListActionsMixin,   # Resposta HTMX da Lista
    WeddingFormLayoutMixin,    # Layout do Formulário
    CreateView
):
    model = Wedding
    # form_class e template_name vêm do WeddingFormLayoutMixin

    def get_context_data(self, **kwargs):
        # Chama o get_context_data do WeddingFormLayoutMixin
        context = super().get_context_data(**kwargs)
        # Adiciona o contexto DINÂMICO do modal
        context['modal_title'] = "Novo Casamento"
        context['submit_button_text'] = "Salvar Casamento"
        context['hx_post_url'] = reverse('weddings:create_wedding')
        return context

    def form_valid(self, form):
        form.instance.planner = self.request.user
        form.save()
        # render_wedding_list_response vem do WeddingListActionsMixin
        return self.render_wedding_list_response()


class WeddingUpdateView(
    PlannerOwnershipMixin,     # Segurança (usa get_queryset)
    WeddingListActionsMixin,   # Resposta HTMX da Lista
    WeddingFormLayoutMixin,    # Layout do Formulário
    UpdateView
):
    model = Wedding
    pk_url_kwarg = "id"
    # form_class e template_name vêm do WeddingFormLayoutMixin
    # get_queryset (segurança) vem do PlannerOwnershipMixin

    def get_context_data(self, **kwargs):
        # Chama o get_context_data do WeddingFormLayoutMixin
        context = super().get_context_data(**kwargs)
        # Adiciona o contexto DINÂMICO do modal
        context['modal_title'] = "Editar Casamento"
        context['submit_button_text'] = "Salvar Alterações"
        context['hx_post_url'] = reverse(
            'weddings:edit_wedding',
            kwargs={'id': self.object.pk}
        )
        return context

    def form_valid(self, form):
        form.save()
        # render_wedding_list_response vem do WeddingListActionsMixin
        return self.render_wedding_list_response()


class WeddingDeleteView(
    PlannerOwnershipMixin,     # Segurança (usa get_queryset)
    WeddingListActionsMixin,   # Resposta HTMX da Lista
    DeleteView
):
    model = Wedding
    template_name = "partials/confirm_delete_modal.html"
    pk_url_kwarg = "id"
    # get_queryset (segurança) vem do PlannerOwnershipMixin

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_name'] = str(self.object)
        context['object_type'] = 'o casamento'
        context['hx_post_url'] = reverse(
            'weddings:delete_wedding',
            kwargs={'id': self.object.pk}
        )
        context['hx_target_id'] = '#wedding-list-container'
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        # render_wedding_list_response vem do WeddingListActionsMixin
        return self.render_wedding_list_response()


class UpdateWeddingStatusView(
    PlannerOwnershipMixin,     # Segurança (usa get_queryset)
    WeddingListActionsMixin,   # Resposta HTMX da Lista
    View
):
    model = Wedding  # Informa ao PlannerOwnershipMixin qual model usar
    # get_queryset (segurança) vem do PlannerOwnershipMixin

    def post(self, request, *args, **kwargs):
        try:
            wedding = self.get_queryset().get(pk=self.kwargs['id'])
        except Wedding.DoesNotExist:
            return HttpResponseBadRequest(
                "Casamento não encontrado ou sem permissão."
            )

        new_status = request.POST.get("status")
        valid_statuses = [status[0] for status in Wedding.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return HttpResponseBadRequest(
                "Status inválido ou Model não atualizado."
            )
        wedding.status = new_status
        wedding.save()

        # render_wedding_list_response vem do WeddingListActionsMixin
        return self.render_wedding_list_response(trigger="listUpdated")


class WeddingDetailView(
    PlannerOwnershipMixin,  # APENAS Segurança
    DetailView
):
    model = Wedding
    template_name = "weddings/detail.html"
    context_object_name = "wedding"
    pk_url_kwarg = "wedding_id"
