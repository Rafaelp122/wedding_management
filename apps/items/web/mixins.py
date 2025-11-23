import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import Http404, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404

# Importa os Mixins GENÉRICOS do Core
from apps.core.mixins.auth import OwnerRequiredMixin
from apps.core.mixins.views import BaseHtmxResponseMixin, HtmxUrlParamsMixin
from apps.weddings.models import Wedding

from ..models import Item
from .forms import ItemForm

logger = logging.getLogger(__name__)

# --- Mixins Independentes (Standalone) ---
# Estes mixins são "standalone" (autônomos/independentes) e não
# dependem de outros mixins deste arquivo. Eles podem ser usados
# sozinhos em Views (ex: DetailView) e seguem o
# Princípio da Segregação de Interface (ISP).


class ItemWeddingContextMixin(LoginRequiredMixin):
    """
    Mixin de Contexto e Segurança (Standalone) - OBRIGATÓRIO

    """

    def dispatch(self, request, *args, **kwargs):
        # Se não estiver autenticado, redireciona para o login imediatamente.
        # Isso impede que o código tente usar 'AnonymousUser' nas queries abaixo.
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        # -----------------------------

        wedding_id = self.kwargs.get("wedding_id")
        pk = self.kwargs.get("pk")

        if not wedding_id and not pk:
            logger.error(
                f"URL malformada para ItemWeddingContextMixin: "
                f"Sem 'wedding_id' ou 'pk'. Kwargs: {self.kwargs}"
            )
            return HttpResponseBadRequest("ID do Casamento ou do Item não encontrado.")

        # Caminho 1: Carregar via 'pk' do Item (Update, Delete, Status)
        if pk:
            # Tenta buscar o item ou lança 404 automaticamente
            try:
                # select_related otimiza a query
                item = Item.objects.select_related("wedding__planner").get(pk=pk)
            except Item.DoesNotExist:
                logger.warning(
                    f"Tentativa de acesso a item inexistente (pk={pk}). Usuário: {request.user.id}"
                )
                raise Http404("Item não encontrado.")

            # Checagem de segurança
            if item.wedding.planner != request.user:
                logger.warning(
                    f"SEGURANÇA: Usuário {request.user.id} tentou acessar item {pk} de outro planner."
                )
                return HttpResponseForbidden("Você não tem permissão para acessar este item.")

            self.wedding = item.wedding

        # Caminho 2: Carregar via 'wedding_id' (List, Create)
        elif wedding_id:
            # get_object_or_404 já lida com DoesNotExist -> 404
            # Filtramos por planner=request.user para garantir segurança
            self.wedding = get_object_or_404(
                Wedding, id=wedding_id, planner=self.request.user
            )

        # Sucesso
        return super().dispatch(request, *args, **kwargs)


class ItemPlannerSecurityMixin(OwnerRequiredMixin):
    """
    Mixin de Segurança 'get_queryset' (Standalone)

    Fornece o 'get_queryset' de segurança para as views
    genéricas (UpdateView, DeleteView).
    """

    model = Item
    # Usa a busca aninhada para checar o "dono"
    owner_field_name = "wedding__planner"


class ItemFormLayoutMixin:
    """
    Mixin de Layout de Formulário (Standalone)

    Define o layout estático para o formulário de Item.
    Assume que 'self.wedding' já existe no contexto (fornecido
    pelo 'ItemWeddingContextMixin').
    """

    form_class = ItemForm
    template_name = "partials/form_modal.html"

    form_layout_dict = {
        "name": "col-6",
        "category": "col-md-6",
        "quantity": "col-md-6",
        "unit_price": "col-md-6",
        "supplier": "col-12",
        "description": "col-12",
    }
    default_col_class = "col-12"
    form_icons = {
        "name": "fas fa-gift",
        "category": "fas fa-tags",
        "quantity": "fas fa-hashtag",
        "unit_price": "fas fa-dollar-sign",
        "supplier": "fas fa-user-tie",
        "description": "fas fa-align-left",
    }

    def get_context_data(self, **kwargs):
        """
        Adiciona o layout (ícones, classes) e o objeto 'wedding'
        ao contexto do template do formulário.
        """
        ctx = super().get_context_data(**kwargs)
        # Assume que 'self.wedding' foi injetado pelo ItemWeddingContextMixin
        ctx["wedding"] = self.wedding
        ctx["form_layout_dict"] = self.form_layout_dict
        ctx["default_col_class"] = self.default_col_class
        ctx["form_icons"] = self.form_icons
        return ctx


# --- Mixins Granulares de Lógica de Lista ---
# Estes mixins são "fine-grained" (granulares) e seguem o
# Princípio da Responsabilidade Única (SRP).
# Cada um é responsável por uma única parte da "lógica de lista".


class ItemQuerysetMixin:
    """
    Fine-Grained Mixin: Query Logic

    Responsável por construir o queryset de 'Item' (busca, filtro, sort).
    Assume que 'self.wedding' existe.
    """

    def get_base_queryset(self, sort="id", q=None, category=None):
        """
        Constrói o queryset base para 'Item' FILTRADO por 'self.wedding'.

        Aplica filtros de categoria, busca (q) e ordenação (sort).

        Args:
            sort (str): O campo de ordenação.
            q (str, optional): O termo de busca.
            category (str, optional): O filtro de categoria.

        Returns:
            QuerySet: O queryset filtrado e ordenado.
        """
        # Começa com os itens APENAS deste casamento
        queryset = Item.objects.filter(wedding=self.wedding)

        if category:
            queryset = queryset.filter(category=category)

        # Assume que o Manager/QuerySet de Item tem
        # os métodos .apply_search() e .apply_sort()
        queryset = queryset.apply_search(q).apply_sort(sort)
        return queryset


class ItemPaginationContextMixin:
    """
    Fine-Grained Mixin: Pagination & Context

    Pagina e formata o contexto da lista.
    Depende de 'get_base_queryset' e 'self.wedding'.
    """

    paginate_by = 6

    def build_paginated_context(self, request_params):
        """
        Constrói o contexto completo para a lista de itens.

        Este é o "cérebro" da paginação:
        1. Obtém os parâmetros da request.
        2. Chama get_base_queryset() para filtrar e ordenar.
        3. Pagina os resultados.
        4. Formata o contexto final para o template.

        Args:
            request_params (dict): Um dicionário de query params
                                   (ex: page, sort, q, category).

        Returns:
            dict: Um contexto pronto para ser usado no template.
        """
        page = request_params.get("page", 1)
        sort = request_params.get("sort", "id")
        q = request_params.get("q", None)
        category = request_params.get("category", None)

        # Loga os parâmetros de entrada
        logger.debug(
            f"Construindo contexto de lista de itens: "
            f"page={page}, sort={sort}, q={q}, category={category}"
        )

        # Dependência: chama get_base_queryset()
        qs = self.get_base_queryset(sort=sort, q=q, category=category)
        paginator = Paginator(qs, self.paginate_by)
        page_obj = paginator.get_page(page)

        elided_page_range = paginator.get_elided_page_range(
            number=page_obj.number,
            on_each_side=2,
            on_ends=1,
        )

        return {
            "wedding": self.wedding,
            "page_obj": page_obj,
            "items": page_obj.object_list,
            "elided_page_range": elided_page_range,
            "current_sort": sort,
            "current_search": q or "",
            "current_category": category or "",
            "request": self.request,
        }


class ItemHtmxListResponseMixin(
    BaseHtmxResponseMixin,
    HtmxUrlParamsMixin,
    ItemPaginationContextMixin,  # Dependência explícita
):
    """
    Fine-Grained Mixin: HTMX Connector

    Conecta a lógica de 'Item' ao renderizador HTMX genérico.
    Usado para renderizar a lista após POST/PUT/DELETE.
    """

    htmx_template_name = "items/partials/_list_and_pagination.html"
    htmx_retarget_id = "#item-list-container"
    htmx_reswap_method = "innerHTML"

    def get_htmx_context_data(self, **kwargs):
        """
        Prepara o contexto para a resposta HTMX (usado após POST/PUT).

        Busca os parâmetros da URL do header HTMX e os utiliza para
        re-construir o contexto de paginação.
        """
        # _get_params_from_htmx_url vem de HtmxUrlParamsMixin
        params = self._get_params_from_htmx_url()

        # build_paginated_context vem de ItemPaginationContextMixin
        context = self.build_paginated_context(params)

        # Precisamos injetar manualmente as variáveis que o template de paginação 
        # espera, pois o 'ItemListView.get_context_data' não é chamado 
        # nas views de Create/Update/Delete.
        context.update({
            "pagination_url_name": "items:partial_items",
            "pagination_target": "#item-list-container",
            "pagination_aria_label": "Paginação de Itens",
        })

        return context

    def render_item_list_response(self, trigger="listUpdated"):
        """
        Helper para renderizar a resposta HTMX da lista de itens.

        Este é o método que as Views (Create/Update/Delete) chamarão.

        Args:
            trigger (str): O nome do evento HTMX a ser disparado.

        Returns:
            HttpResponse: A resposta HTMX renderizada.
        """
        return self.render_htmx_response(trigger=trigger)


# --- Mixin de Composição (Facade Pattern) ---


class ItemListActionsMixin(
    ItemQuerysetMixin,
    ItemHtmxListResponseMixin,  # Já inclui o ItemPaginationContextMixin
):
    """
    Mixin de Composição (Composition Mixin)

    Atua como uma "fachada" (Facade Pattern) que agrupa
    a lógica de lista (Query, Paginação, HTMX).
    """

    pass
