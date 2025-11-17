import logging

from django.core.paginator import Paginator

from apps.core.constants import GRADIENTS
from apps.core.mixins.auth import OwnerRequiredMixin
from apps.core.mixins.views import BaseHtmxResponseMixin, HtmxUrlParamsMixin

from .forms import WeddingForm
from .models import Wedding

logger = logging.getLogger(__name__)

# --- Mixins Independentes (Standalone) ---
# Estes mixins são "standalone" (autônomos/independentes) e não
# dependem de outros mixins deste arquivo. Eles podem ser usados
# sozinhos em Views (ex: DetailView) e seguem o
# Princípio da Segregação de Interface (ISP).


class PlannerOwnershipMixin(OwnerRequiredMixin):
    """Define model e owner_field_name para o OwnerRequiredMixin."""
    model = Wedding
    owner_field_name = "planner"


class WeddingFormLayoutMixin:
    """
    Domain-Specific Form Layout Mixin (Standalone)

    Define o layout estático, ícones e classes (lógica de
    apresentação específica) para o formulário de Wedding.
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
        """
        Adiciona as variáveis de layout (dicionários, classes)
        ao contexto do template do formulário.
        """
        ctx = super().get_context_data(**kwargs)
        ctx["form_layout_dict"] = self.form_layout_dict
        ctx["default_col_class"] = self.default_col_class
        ctx["form_icons"] = self.form_icons
        return ctx


# --- Mixins Granulares de Lógica de Lista ---
# Estes mixins são "fine-grained" (granulares) e seguem o
# Princípio da Responsabilidade Única (SRP).
# Cada um é responsável por uma única parte da "lógica de lista".


class WeddingQuerysetMixin:
    """
    Fine-Grained Mixin: Query Logic

    Responsável *apenas* por construir o queryset de 'Wedding'.
    (lógica de dados específica).
    """

    def get_base_queryset(self, sort="id", q=None, status=None):
        """
        Constrói o queryset base para 'Wedding' logado.

        Aplica filtros de planner, status, busca (q) e
        ordenação (sort), além de anotar contagens.

        Args:
            sort (str): O campo de ordenação.
            q (Optional[str]): O termo de busca.
            status (Optional[str]): O filtro de status.

        Returns:
            QuerySet: O queryset filtrado e anotado.
        """
        queryset = Wedding.objects.filter(planner=self.request.user)
        queryset = queryset.with_effective_status().apply_search(q).apply_sort(sort)
        if status:
            queryset = queryset.filter(effective_status=status)
        queryset = queryset.with_counts_and_progress()
        return queryset


class WeddingPaginationContextMixin:
    """
    Fine-Grained Mixin: Pagination & Context

    Responsável *apenas* por paginar o queryset e formatar
    o contexto final. Possui uma *dependência* implícita do
    'get_base_queryset' (fornecido pelo WeddingQuerysetMixin).
    """

    paginate_by = 6

    def _build_context_list(self, queryset):
        """
        Formata a lista de 'Wedding' para o template.

        Adiciona dados contextuais (ex: gradientes, contagens)
        que não são necessários na paginação pura.
        """
        return [
            {
                "wedding": wedding,
                "gradient": GRADIENTS[idx % len(GRADIENTS)],
                "items_count": wedding.items_count,
                "contracts_count": wedding.contracts_count,
                "effective_status": wedding.effective_status,
                "progress": wedding.progress,
            }
            for idx, wedding in enumerate(queryset)
        ]

    def build_paginated_context(self, request_params):
        """
        Constrói o contexto completo para a lista de casamentos.

        Este método é o "núcleo" da paginação:
        1. Obtém os parâmetros da request.
        2. Chama get_base_queryset() para filtrar e ordenar.
        3. Pagina os resultados.
        4. Formata o contexto final para o template.

        Args:
            request_params (dict): Um dicionário de query params (ex: page, sort, q).

        Returns:
            dict: Um contexto pronto para ser usado no template.
        """
        page = request_params.get("page", 1)
        sort = request_params.get("sort", "id")
        q = request_params.get("q", None)
        status = request_params.get("status", None)

        logger.debug(
            f"Construindo contexto: page={page}, sort={sort}, q={q}, status={status}"
        )

        # Dependência: chama get_base_queryset()
        qs = self.get_base_queryset(sort=sort, q=q, status=status)

        paginator = Paginator(qs, self.paginate_by)
        page_obj = paginator.get_page(page)

        elided_page_range = paginator.get_elided_page_range(
            number=page_obj.number,
            on_each_side=3,  # Ex: 1 ... 4 [5] 6 ... 50
            on_ends=1,
        )

        paginated_weddings_formatted = self._build_context_list(
            queryset=page_obj.object_list
        )

        return {
            "page_obj": page_obj,
            "paginated_weddings": paginated_weddings_formatted,
            "elided_page_range": elided_page_range,
            "current_sort": sort,
            "current_search": q or "",
            "current_status": status or "",
            "request": self.request,
        }


class WeddingHtmxListResponseMixin(
    BaseHtmxResponseMixin,
    HtmxUrlParamsMixin,
    WeddingPaginationContextMixin,
):
    """
    Fine-Grained Mixin: HTMX Connector

    Atua como um "conector" que define o template/target específicos
    para o 'BaseHtmxResponseMixin' genérico.

    Possui uma *dependência* direta do 'WeddingPaginationContextMixin'
    para obter o 'build_paginated_context'.
    """

    htmx_template_name = "weddings/partials/_list_and_pagination.html"
    htmx_retarget_id = "#wedding-list-container"

    def get_htmx_context_data(self, **kwargs):
        """
        Prepara o contexto para a resposta HTMX.

        Busca os parâmetros da URL do HTMX e os utiliza para
        construir o contexto de paginação.
        """
        params = self._get_params_from_htmx_url()
        context = self.build_paginated_context(params)
        return context

    def render_wedding_list_response(self, trigger="listUpdated"):
        """
        Helper para renderizar a resposta HTMX da lista de casamentos.

        Args:
            trigger (str): O nome do evento HTMX a ser disparado.

        Returns:
            HttpResponse: A resposta HTMX renderizada.
        """
        return self.render_htmx_response(trigger=trigger)


# --- Mixin de Composição (Facade Pattern) ---


class WeddingListActionsMixin(WeddingQuerysetMixin, WeddingHtmxListResponseMixin):
    """
    Mixin de Composição (Composition Mixin)

    Este mixin não implementa lógica nova. Ele atua como uma "fachada"
    (Facade Pattern) que agrupa os mixins granulares
    (Queryset, Pagination, HTMX) em uma única interface.

    O objetivo é puramente de conveniência e de seguir o princípio DRY
    (Don't Repeat Yourself) nas Views: em vez de uma View herdar
    3 ou 4 mixins de lista, ela herda apenas este.
    """

    pass
