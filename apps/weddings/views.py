from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from apps.core.utils.constants import GRADIENTS

from .forms import WeddingForm
from .models import Wedding


class WeddingBaseMixin(LoginRequiredMixin):
    """
    Unifica:
    - filtro por planner
    - order_by
    - annotate (items_count, contracts_count)
    - geração de weddings_with_clients
    - renderização HTMX da lista
    """

    def get_queryset(self):
        """
        Método de segurança padrão (usado por UpdateView, DeleteView).
        Garante que o usuário só pode operar em seus próprios objetos.
        """
        queryset = super().get_queryset()
        return queryset.filter(planner=self.request.user)

    def get_base_queryset(self):
        sort_option = self.request.GET.get('sort', 'id')
        search_query = self.request.GET.get('q', None)

        # 2. Queryset base (planner)
        queryset = Wedding.objects.filter(planner=self.request.user)

        # Aplica o filtro de BUSCA (se existir)
        if search_query:
            queryset = queryset.filter(
                Q(groom_name__icontains=search_query) |
                Q(bride_name__icontains=search_query)
            )

        if sort_option == 'date_desc':
            order_by_field = '-date'
        elif sort_option == 'date_asc':
            order_by_field = 'date'
        elif sort_option == 'name_asc':
            order_by_field = 'groom_name'
        else:
            order_by_field = 'id'

        return (
            queryset
            .order_by(order_by_field)
            .annotate(
                items_count=Count("item", distinct=True),
                contracts_count=Count("contract", distinct=True),
            )
        )

    def build_weddings_with_clients(self, queryset=None):
        qs = queryset if queryset is not None else self.get_base_queryset()
        return [
            {
                "wedding": wedding,
                "gradient": GRADIENTS[idx % len(GRADIENTS)],
                "items_count": wedding.items_count,
                "contracts_count": wedding.contracts_count,
            }
            for idx, wedding in enumerate(qs)
        ]

    def render_wedding_list_response(self, trigger="weddingCreated"):
        context = {"weddings_with_clients": self.build_weddings_with_clients()}
        html = render_to_string(
            "weddings/partials/_wedding_list_content.html",
            context,
            request=self.request,
        )

        response = HttpResponse(html)
        response["HX-Retarget"] = "#wedding-list-container"
        response["HX-Reswap"] = "innerHTML"
        response["HX-Trigger-After-Swap"] = trigger
        return response


class WeddingFormLayoutMixin:
    """
    Define o layout e ícones para o formulário de Casamento.
    """
    form_class = WeddingForm
    template_name = "weddings/partials/_create_wedding_form.html"

    form_layout_dict = {
        "groom_name": "col-md-6",
        "bride_name": "col-md-6",
        "date": "col-md-6",
        "location": "col-md-12",
        "budget": "col-md-6",
    }
    default_col_class = "col-12"
    form_icons = {
        "groom_name": "fas fa-user",
        "bride_name": "fas fa-user",
        "date": "fas fa-calendar-days",
        "location": "fas fa-location-dot",
        "budget": "fas fa-money-bill-wave",
    }

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["form_layout_dict"] = self.form_layout_dict
        ctx["default_col_class"] = self.default_col_class
        ctx["form_icons"] = self.form_icons
        return ctx


class WeddingListView(WeddingBaseMixin, ListView):
    model = Wedding
    template_name = "weddings/list.html"
    context_object_name = "weddings"

    def get_queryset(self):
        # Usa o método do Mixin
        return self.get_base_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adiciona o contexto da lista ('weddings_with_clients') do Mixin
        context.update(
            {"weddings_with_clients": self.build_weddings_with_clients()}
        )
        return context

    def render_to_response(self, context, **response_kwargs):
        """
        Sobrescreve o método de renderização para lidar com
        requisições HTMX.
        """
        # Verifica se o request foi feito pelo HTMX
        if self.request.htmx:
            # Se for, renderiza APENAS o partial da lista.
            # O 'context' já foi preparado pelo get_context_data.
            return render(
                self.request,
                "weddings/partials/_wedding_list_content.html",
                context
            )

        # Se for um carregamento de página normal,
        # renderiza a página inteira (list.html)
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
