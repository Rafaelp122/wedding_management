import logging
from typing import Any, Dict, List

from django.core.paginator import Paginator
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse

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
    """
    Define model e owner_field_name para o OwnerRequiredMixin.

    Este mixin especializa o OwnerRequiredMixin genérico para o modelo
    Wedding, configurando os atributos necessários.

    Usage:
        class MyWeddingView(PlannerOwnershipMixin, UpdateView):
            fields = ['date', 'location', 'budget']
    """

    model = Wedding
    owner_field_name = "planner"


class WeddingFormLayoutMixin:
    """
    Domain-Specific Form Layout Mixin (Standalone)

    Define o layout estático, ícones e classes (lógica de
    apresentação específica) para o formulário de Wedding.

    Este mixin adiciona informações de apresentação ao contexto
    do template, como classes CSS para layout responsivo e
    ícones Font Awesome para cada campo.

    Attributes:
        form_class: Classe do formulário Django.
        template_name: Nome do template a ser renderizado.
        form_layout_dict: Dicionário com classes CSS Bootstrap
                         para cada campo.
        default_col_class: Classe CSS padrão para campos
                          não especificados.
        form_icons: Dicionário com ícones Font Awesome para
                   cada campo.
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

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Adiciona as variáveis de layout (dicionários, classes)
        ao contexto do template do formulário.

        Args:
            **kwargs: Argumentos de contexto adicionais.

        Returns:
            Dicionário com o contexto completo incluindo dados
            de layout.
        """
        ctx = super().get_context_data(**kwargs)  # type: ignore[misc]
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

    Este mixin encapsula toda a lógica de filtragem, busca e
    ordenação de casamentos, utilizando os métodos personalizados
    do QuerySet Manager.

    Attributes:
        request: HttpRequest object (deve ser fornecido pela View).
    """

    request: HttpRequest

    def get_base_queryset(
        self, sort: str = "id", q: str | None = None, status: str | None = None
    ) -> "QuerySet[Any, Any]":
        """
        Constrói o queryset base para 'Wedding' logado.

        Aplica filtros de planner, status, busca (q) e
        ordenação (sort), além de anotar contagens.

        Args:
            sort: O campo de ordenação (default: 'id').
            q: O termo de busca (opcional).
            status: O filtro de status (opcional).

        Returns:
            QuerySet filtrado, anotado e ordenado de Wedding.
        """
        queryset = Wedding.objects.filter(planner=self.request.user)
        # type: ignore - métodos customizados do WeddingQuerySet
        queryset = (  # type: ignore[assignment]
            queryset.with_effective_status()  # type: ignore[attr-defined]
            .apply_search(q)  # type: ignore[attr-defined]
            .apply_sort(sort)  # type: ignore[attr-defined]
        )
        if status:
            # type: ignore - filtragem customizada
            queryset = queryset.filter(  # type: ignore[assignment]
                effective_status=status
            )
        # type: ignore - método customizado do WeddingQuerySet
        queryset = queryset.with_counts_and_progress()  # type: ignore[assignment,attr-defined]
        return queryset  # type: ignore[return-value]


class WeddingPaginationContextMixin:
    """
    Fine-Grained Mixin: Pagination & Context

    Responsável *apenas* por paginar o queryset e formatar
    o contexto final. Possui uma *dependência* implícita do
    'get_base_queryset' (fornecido pelo WeddingQuerysetMixin).

    Este mixin formata os dados de wedding para exibição,
    adicionando informações visuais como gradientes e contadores.

    Attributes:
        paginate_by: Número de itens por página.
        request: HttpRequest object (deve ser fornecido pela View).
    """

    paginate_by = 6
    request: HttpRequest

    def _build_context_list(
        self, queryset: Any
    ) -> List[Dict[str, Any]]:
        """
        Formata a lista de 'Wedding' para o template.

        Adiciona dados contextuais (ex: gradientes, contagens)
        que não são necessários na paginação pura.

        Args:
            queryset: QuerySet ou lista de Wedding a ser formatado.

        Returns:
            Lista de dicionários com dados formatados para o template.

        Note:
            Aceita Any devido à incompatibilidade de tipos entre
            Page.object_list e QuerySet no sistema de tipos.
        """
        return [
            {
                "wedding": wedding,
                "gradient": GRADIENTS[idx % len(GRADIENTS)],
                # type: ignore - campos anotados pelo QuerySet
                "items_count": (
                    wedding.items_count  # type: ignore[attr-defined]
                ),
                "contracts_count": (
                    wedding.contracts_count  # type: ignore[attr-defined]
                ),
                "effective_status": (
                    wedding.effective_status  # type: ignore[attr-defined]
                ),
                "progress": wedding.progress,  # type: ignore[attr-defined]
            }
            for idx, wedding in enumerate(queryset)
        ]

    def build_paginated_context(
        self, request_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Constrói o contexto completo para a lista de casamentos.

        Este método é o "núcleo" da paginação:
        1. Obtém os parâmetros da request.
        2. Chama get_base_queryset() para filtrar e ordenar.
        3. Pagina os resultados.
        4. Formata o contexto final para o template.

        Args:
            request_params: Um dicionário de query params
                           (ex: page, sort, q, status).

        Returns:
            Dicionário com contexto pronto para o template.
        """
        page = request_params.get("page", 1)
        sort = request_params.get("sort", "id")
        q = request_params.get("q", None)
        status = request_params.get("status", None)

        logger.debug(
            f"Construindo contexto: page={page}, sort={sort}, "
            f"q={q}, status={status}"
        )

        # Dependência: chama get_base_queryset()
        # type: ignore - método fornecido por WeddingQuerysetMixin
        qs = self.get_base_queryset(  # type: ignore[attr-defined]
            sort=sort, q=q, status=status
        )

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

    Este mixin conecta a lógica de paginação de Wedding com o
    sistema de respostas HTMX genérico do core.

    Attributes:
        htmx_template_name: Template parcial para lista de weddings.
        htmx_retarget_id: ID do container alvo no DOM.
    """

    htmx_template_name = "weddings/partials/_list_and_pagination.html"
    htmx_retarget_id = "#wedding-list-container"

    def get_htmx_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Prepara o contexto para a resposta HTMX.

        Busca os parâmetros da URL do HTMX e os utiliza para
        construir o contexto de paginação.

        Args:
            **kwargs: Argumentos de contexto adicionais (ignorados).

        Returns:
            Dicionário com contexto completo para o template.
        """
        params = self._get_params_from_htmx_url()
        context = self.build_paginated_context(params)
        return context

    def render_wedding_list_response(
        self, trigger: str = "listUpdated"
    ) -> HttpResponse:
        """
        Helper para renderizar a resposta HTMX da lista de casamentos.

        Args:
            trigger: O nome do evento HTMX a ser disparado
                    (default: 'listUpdated').

        Returns:
            HttpResponse com HTML renderizado e headers HTMX.
        """
        return self.render_htmx_response(trigger=trigger)


# --- Mixin de Composição (Facade Pattern) ---


class WeddingListActionsMixin(
    WeddingQuerysetMixin, WeddingHtmxListResponseMixin
):
    """
    Mixin de Composição (Composition Mixin)

    Este mixin não implementa lógica nova. Ele atua como uma "fachada"
    (Facade Pattern) que agrupa os mixins granulares
    (Queryset, Pagination, HTMX) em uma única interface.

    O objetivo é puramente de conveniência e de seguir o princípio DRY
    (Don't Repeat Yourself) nas Views: em vez de uma View herdar
    3 ou 4 mixins de lista, ela herda apenas este.

    Usage:
        class WeddingListView(WeddingListActionsMixin, ListView):
            # Acesso a get_base_queryset, build_paginated_context,
            # e render_wedding_list_response em uma única herança
            pass
    """

    pass
