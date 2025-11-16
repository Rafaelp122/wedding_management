from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404

# Importa os Mixins GENÉRICOS do Core
from apps.core.mixins.auth import OwnerRequiredMixin
from apps.core.mixins.views import BaseHtmxResponseMixin, HtmxUrlParamsMixin
from apps.weddings.models import Wedding

from .forms import ItemForm
from .models import Item


# --- Mixins Independentes (Standalone) ---
# Estes mixins são "standalone" (autônomos/independentes) e não
# dependem de outros mixins deste arquivo. Eles podem ser usados
# sozinhos em Views (ex: DetailView) e seguem o
# Princípio da Segregação de Interface (ISP).

class ItemWeddingContextMixin(LoginRequiredMixin):
    """
    Mixin de Contexto e Segurança (Standalone) - OBRIGATÓRIO

    Este é o mixin mais importante do app 'items'. Sua única
    responsabilidade é carregar 'self.wedding' ANTES de qualquer
    outra lógica da view (via 'dispatch').

    Ele garante que 'self.wedding' está sempre disponível e que
    o usuário tem permissão para acessá-lo.
    """
    def dispatch(self, request, *args, **kwargs):
        """
        Busca o Casamento ANTES de qualquer outra coisa.
        """
        wedding_id = self.kwargs.get("wedding_id")

        if not wedding_id:
            # Se não houver 'wedding_id' na URL, a view deve ser
            # de um item existente (Edit, Delete, UpdateStatus).
            if 'pk' in self.kwargs:
                try:
                    item = Item.objects.select_related('wedding__planner').get(
                        pk=self.kwargs['pk']
                    )
                    # Checagem de segurança
                    if item.wedding.planner != self.request.user:
                        return HttpResponseBadRequest("Permissão negada.")
                    self.wedding = item.wedding
                except Item.DoesNotExist:
                    return HttpResponseBadRequest("Item não encontrado.")
            else:
                return HttpResponseBadRequest(
                    "ID do Casamento ou do Item não encontrado."
                )
        else:
            # Se 'wedding_id' está na URL (ListView, AddItemView),
            # busca o casamento e já checa a segurança.
            self.wedding = get_object_or_404(
                Wedding,
                id=wedding_id,
                planner=self.request.user
            )
        return super().dispatch(request, *args, **kwargs)


class ItemPlannerSecurityMixin(OwnerRequiredMixin):
    """
    Mixin de Segurança 'get_queryset' (Standalone)

    Fornece o 'get_queryset' de segurança para as views
    genéricas (UpdateView, DeleteView).
    """
    model = Item
    # Usa a busca aninhada para checar o "dono"
    owner_field_name = 'wedding__planner'


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
    def get_base_queryset(self, sort='id', q=None, category=None):
        # Começa com os itens APENAS deste casamento
        queryset = Item.objects.filter(wedding=self.wedding)

        if category:
            queryset = queryset.filter(category=category)

        queryset = (
            queryset
            .apply_search(q)
            .apply_sort(sort)
        )
        return queryset.select_related("supplier")


class ItemPaginationContextMixin:
    """
    Fine-Grained Mixin: Pagination & Context

    Pagina e formata o contexto da lista.
    Depende de 'get_base_queryset' e 'self.wedding'.
    """
    paginate_by = 6

    def build_paginated_context(self, request_params):
        page = request_params.get('page', 1)
        sort = request_params.get('sort', 'id')
        q = request_params.get('q', None)
        category = request_params.get('category', None)

        # Dependência: chama get_base_queryset()
        qs = self.get_base_queryset(sort=sort, q=q, category=category)
        paginator = Paginator(qs, self.paginate_by)
        page_obj = paginator.get_page(page)

        elided_page_range = paginator.get_elided_page_range(
            number=page_obj.number,
            on_each_side=2,  # Um valor curto é melhor para listas de itens
            on_ends=1
        )

        return {
            "wedding": self.wedding,
            "page_obj": page_obj,
            "items": page_obj.object_list,
            "elided_page_range": elided_page_range,
            "current_sort": sort,
            "current_search": q or '',
            "current_category": category or '',
            "request": self.request
        }


class ItemHtmxListResponseMixin(
    BaseHtmxResponseMixin,
    HtmxUrlParamsMixin,
    ItemPaginationContextMixin  # Dependência explícita
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
        Hook do Base: Pega o estado da URL (dos headers) e
        constrói o contexto de paginação.
        """
        # _get_params_from_htmx_url vem de HtmxUrlParamsMixin
        params = self._get_params_from_htmx_url()

        # build_paginated_context vem de ItemPaginationContextMixin
        context = self.build_paginated_context(params)
        return context

    def render_item_list_response(self, trigger="listUpdated"):
        """
        Método de conveniência que as Views (Create/Update/Delete) chamarão.
        """
        return self.render_htmx_response(trigger=trigger)


# --- Mixin de Composição (Facade Pattern) ---

class ItemListActionsMixin(
    ItemQuerysetMixin,
    ItemHtmxListResponseMixin  # Já inclui o ItemPaginationContextMixin
):
    """
    Mixin de Composição (Composition Mixin)

    Atua como uma "fachada" (Facade Pattern) que agrupa
    a lógica de lista (Query, Paginação, HTMX).
    """
    pass
