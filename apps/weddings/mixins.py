from urllib.parse import parse_qs, urlparse

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.template.loader import render_to_string

from apps.core.constants import GRADIENTS

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

    # Define a quantidade de itens por página
    paginate_by = 6

    def get_queryset(self):
        """
        Método de segurança padrão (usado por UpdateView, DeleteView).
        Garante que o usuário só pode operar em seus próprios objetos.
        """

        if not hasattr(self, 'model'):
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} is missing a 'model' attribute."
            )

        queryset = self.model.objects.all()

        return queryset.filter(planner=self.request.user)

    def get_base_queryset(self, sort='id', q=None, status=None):
        """
        Pega o queryset base e chama os helpers do model
        para aplicar lógica.
        """

        queryset = Wedding.objects.filter(planner=self.request.user)

        # Chama os helpers do Model
        queryset = (
            queryset
            .with_effective_status()  # Anota o status
            .apply_search(q)          # Aplica a busca
            .apply_sort(sort)         # Aplica a ordenação
        )

        # Aplica o filtro de status (se existir)
        if status:
            queryset = queryset.filter(effective_status=status)

        # Chama o helper de contagem/progresso do Model
        queryset = queryset.with_counts_and_progress()

        return queryset

    def _build_context_list(self, queryset):
        """
        Helper "privado" que apenas formata a lista de objetos
        para o contexto do template.
        """
        return [
            {
                "wedding": wedding,
                "gradient": GRADIENTS[idx % len(GRADIENTS)],
                "items_count": wedding.items_count,
                "contracts_count": wedding.contracts_count,
                "effective_status": wedding.effective_status,
                "progress": wedding.progress,  # É do with_counts_and_progress
            }
            for idx, wedding in enumerate(queryset)
        ]

    def build_paginated_context(self, request_params):
        """
        Pega os parâmetros (do GET ou POST), pagina
        e formata o contexto.
        """
        # Pega o estado (página, filtro, busca) dos parâmetros
        page = request_params.get('page', 1)
        sort = request_params.get('sort', 'id')
        q = request_params.get('q', None)
        status = request_params.get('status', None)

        # Pega o queryset filtrado e ordenado
        qs = self.get_base_queryset(sort=sort, q=q, status=status)

        # Pagina o queryset
        paginator = Paginator(qs, self.paginate_by)
        page_obj = paginator.get_page(page)

        # Formata OS ITENS DA PÁGINA ATUAL
        paginated_weddings_formatted = self._build_context_list(
            queryset=page_obj.object_list
        )

        # Retorna o contexto completo que os parciais precisam
        return {
            "page_obj": page_obj,
            "paginated_weddings": paginated_weddings_formatted,
            "current_sort": sort,
            "current_search": q or '',
            "current_status": status or '',
            "request": self.request,
        }

    def render_wedding_list_response(self, trigger="listUpdated"):
        """
        Renderiza a resposta HTMX para Create/Update/Delete.
        Lê o 'HX-Current-Url' para preservar o estado.
        """
        # Pega a URL que o usuário estava vendo (do header HTMX)
        current_url = self.request.headers.get('Hx-Current-Url')
        params = {}
        if current_url:
            try:
                # Parseia a URL para extrair os query params
                query_string = urlparse(current_url).query
                parsed_params = parse_qs(query_string)
                params = {k: v[0] for k, v in parsed_params.items()}
            except Exception:
                pass  # Se falhar, usa os defaults (page=1, etc)

        # Constrói o contexto com o estado correto
        context = self.build_paginated_context(params)

        # Renderiza o partial
        html = render_to_string(
            "weddings/partials/_list_and_pagination.html",
            context,
            request=self.request,
        )

        response = HttpResponse(html)
        response["HX-Retarget"] = '#wedding-list-container'
        response["HX-Reswap"] = 'innerHTML'

        response["HX-Trigger-After-Swap"] = trigger
        return response


class WeddingFormLayoutMixin:
    """
    Define o layout e ícones para o formulário de Casamento.
    """
    form_class = WeddingForm
    template_name = "partials/form_modal.html"

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
