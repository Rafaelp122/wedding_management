from django.core.paginator import Paginator

from apps.core.mixins.auth import OwnerRequiredMixin
from apps.core.mixins.views import BaseHtmxResponseMixin, HtmxUrlParamsMixin
from apps.core.constants import GRADIENTS

from .forms import WeddingForm
from .models import Wedding


# --- Mixins Independentes (Standalone) ---
# Estes mixins são "standalone" (autônomos/independentes) e não
# dependem de outros mixins deste arquivo. Eles podem ser usados
# sozinhos em Views (ex: DetailView) e seguem o
# Princípio da Segregação de Interface (ISP).


class PlannerOwnershipMixin(OwnerRequiredMixin):
    """
    Domain-Specific Security Mixin (Standalone)

    Define o 'model' e 'owner_field_name' (lógica de negócio específica)
    para o 'OwnerRequiredMixin' (lógica genérica do core).
    """

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
        page = request_params.get("page", 1)
        sort = request_params.get("sort", "id")
        q = request_params.get("q", None)
        status = request_params.get("status", None)

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
    WeddingPaginationContextMixin,  # Dependência explícita
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
        # Dependência: chama _get_params_from_htmx_url()
        params = self._get_params_from_htmx_url()

        # Dependência: chama build_paginated_context()
        context = self.build_paginated_context(params)
        return context

    def render_wedding_list_response(self, trigger="listUpdated"):
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
