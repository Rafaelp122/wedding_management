from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)

from .mixins import WeddingBaseMixin, WeddingFormLayoutMixin
from .models import Wedding


class WeddingListView(WeddingBaseMixin, ListView):
    model = Wedding
    template_name = "weddings/list.html"
    context_object_name = "weddings"
    paginate_by = 6

    def get_queryset(self):
        # Usa o 'get_base_queryset' do Mixin para
        # pegar a lista já filtrada/buscada/ordenada.
        # O ListView vai paginar este queryset.
        return self.get_base_queryset()

    def get_context_data(self, **kwargs):
        # 'super().get_context_data()' é chamado primeiro.
        # Executa a paginação e coloca 'page_obj' no contexto.
        context = super().get_context_data(**kwargs)

        context.update(
            self.build_paginated_context(self.request.GET)
        )

        # Passa os filtros/busca atuais para os links de paginação
        context['current_sort'] = self.request.GET.get('sort', 'id')
        context['current_search'] = self.request.GET.get('q', '')
        context['request'] = self.request

        return context

    def render_to_response(self, context, **response_kwargs):
        # Lida com as requisições HTMX (filtro, busca, paginação)
        if self.request.htmx:
            # Renderiza o partial que contém a LISTA + PAGINAÇÃO (OOB)
            return render(
                self.request,
                "weddings/partials/_list_and_pagination.html",
                context
            )

        # Se for um F5, renderiza a página inteira
        return super().render_to_response(context, **response_kwargs)


class WeddingCreateView(WeddingBaseMixin, WeddingFormLayoutMixin, CreateView):
    model = Wedding
    # form_class e template_name vêm do WeddingFormLayoutMixin
    # get_context_data vem do WeddingFormLayoutMixin

    def form_valid(self, form):
        form.instance.planner = self.request.user
        form.save()
        # Retorna a resposta HTMX completa do Mixin
        return self.render_wedding_list_response()


class WeddingUpdateView(WeddingFormLayoutMixin, WeddingBaseMixin, UpdateView):
    model = Wedding
    pk_url_kwarg = "id"
    # form_class e template_name vêm do WeddingFormLayoutMixin
    # get_context_data vem do WeddingFormLayoutMixin

    def form_valid(self, form):
        form.save()
        # Retorna a resposta HTMX completa do Mixin
        return self.render_wedding_list_response()


class WeddingDeleteView(WeddingBaseMixin, DeleteView):
    model = Wedding
    template_name = "partials/confirm_delete_modal.html"
    pk_url_kwarg = "id"

    def get_context_data(self, **kwargs):
        # Esta view ainda precisa do seu próprio get_context_data
        # para o modal de deleção reutilizável
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
        # Retorna a resposta HTMX completa do Mixin
        return self.render_wedding_list_response()


class UpdateWeddingStatusView(WeddingBaseMixin, View):
    """
    Atualiza o status de um Casamento (Ex: Em Andamento, Concluído).
    Chamada via hx-post a partir do dropdown do card.
    """
    model = Wedding  # Informa ao get_queryset qual model usar

    def post(self, request, *args, **kwargs):

        # Pega o objeto de forma segura
        # 'self.get_queryset()' vem do WeddingBaseMixin
        try:
            # ATENÇÃO: A URL que vamos criar usa 'id', não 'pk'
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

        # Atualiza e salva o casamento
        wedding.status = new_status
        wedding.save()

        # Retorna a lista completa (com paginação/filtros preservados)
        # 'self.render_wedding_list_response()' vem do WeddingBaseMixin
        return self.render_wedding_list_response(trigger="listUpdated")


class WeddingDetailView(DetailView):
    # Esta view não muda, pois é única
    model = Wedding
    template_name = "weddings/detail.html"
    context_object_name = "wedding"
    pk_url_kwarg = "wedding_id"

    def get_queryset(self):
        """
        Garante que o usuário só pode ver seus próprios casamentos.
        """
        queryset = super().get_queryset()
        return queryset.filter(planner=self.request.user)
