from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
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
    - paginação
    - renderização HTMX da lista
    """

    # Define quantos itens por página
    paginate_by = 9

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
        # Pega o queryset completo, filtrado e ordenado
        full_queryset = self.get_base_queryset()

        # Pagina o queryset
        paginator = Paginator(full_queryset, self.paginate_by)
        page_number = self.request.GET.get('page', 1)  # Pega a página da URL
        page_obj = paginator.get_page(page_number)

        # Formata APENAS os itens da página atual
        paginated_weddings_formatted = self.build_weddings_with_clients(
            queryset=page_obj.object_list
        )

        # Constrói o contexto para os parciais
        context = {
            "page_obj": page_obj,
            "paginated_weddings": paginated_weddings_formatted,
            "current_sort": self.request.GET.get('sort', 'id'),
            "current_search": self.request.GET.get('q', ''),
            "request": self.request # Passa o request para o partial (para o ?q=)
        }

        # Renderiza o template que contém a LISTA + PAGINAÇÃO (OOB)
        html = render_to_string(
            "weddings/partials/_list_and_pagination.html",
            context,
            request=self.request,
        )

        response = HttpResponse(html)

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

    # Define o 'paginate_by' (deve ser o mesmo do seu Mixin)
    paginate_by = 9

    def get_queryset(self):
        # Usa o 'get_base_queryset' do Mixin para
        # pegar a lista já filtrada/buscada/ordenada.
        # O ListView vai paginar este queryset.
        return self.get_base_queryset()

    def get_context_data(self, **kwargs):
        # 'super().get_context_data()' é chamado primeiro.
        # Executa a paginação e coloca 'page_obj' no contexto.
        context = super().get_context_data(**kwargs)

        # Pega os 9 itens da página atual
        page_items = context['page_obj'].object_list

        # Formata esses 9 itens usando o método helper do Mixin
        context['paginated_weddings'] = self.build_weddings_with_clients(
            queryset=page_items
        )

        # Passa os filtros/busca atuais para os links de paginação
        context['current_sort'] = self.request.GET.get('sort', 'id')
        context['current_search'] = self.request.GET.get('q', '')
        context['request'] = self.request # Para a mensagem de 'vazio' no partial

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
