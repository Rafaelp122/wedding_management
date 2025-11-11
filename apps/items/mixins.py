from urllib.parse import parse_qs, urlparse

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from apps.weddings.models import Wedding

from .forms import ItemForm
from .models import Item


class ItemBaseMixin(LoginRequiredMixin):
    """
    Unifica toda a lógica do app 'items':
    - Garante que um 'wedding' foi carregado
    - Garante segurança (filtro por planner)
    - Lida com busca, filtro, paginação
    - Renderiza a resposta HTMX OOB (Lista + Paginação)
    """
    paginate_by = 6
    model = Item

    def dispatch(self, request, *args, **kwargs):
        """
        Busca o Casamento ANTES de qualquer outra coisa.
        Isso nos dá 'self.wedding' em todas as views.
        """
        # Tenta pegar o 'wedding_id' da URL (para AddView, ListView)
        wedding_id = self.kwargs.get("wedding_id")

        if not wedding_id:
            # Se não, pega o 'pk' do Item (para EditView, DeleteView)
            # e encontra o casamento através dele
            if 'pk' in self.kwargs:
                try:
                    item = Item.objects.select_related('wedding').get(pk=self.kwargs['pk'])
                    if item.wedding.planner != self.request.user:
                        return HttpResponseBadRequest("Permissão negada.")
                    self.wedding = item.wedding
                except Item.DoesNotExist:
                    return HttpResponseBadRequest("Item não encontrado.")
            else:
                return HttpResponseBadRequest("ID do Casamento não encontrado.")
        else:
            self.wedding = get_object_or_404(
                Wedding,
                id=wedding_id,
                planner=self.request.user
            )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        Método de segurança padrão (usado por UpdateView, DeleteView).
        """
        if not hasattr(self, 'model'):
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} is missing a 'model' attribute."
            )
        queryset = self.model.objects.all()
        # Filtra por planner (segurança)
        return queryset.filter(wedding__planner=self.request.user)

    def get_base_queryset(self, sort='id', q=None, category=None):
        """
        Pega o queryset base de ITENS, filtrado e ordenado.
        """
        # Começa com os itens APENAS deste casamento
        queryset = Item.objects.filter(wedding=self.wedding)

        # Aplica o filtro de CATEGORIA (se existir)
        if category:
            queryset = queryset.filter(category=category)

        # Chama os helpers do Model
        queryset = (
            queryset
            .apply_search(q)   # Aplica a busca
            .apply_sort(sort)  # Aplica a ordenação
        )

        return queryset.select_related("supplier")

    def build_paginated_context(self, request_params):
        """
        Helper central: Pega os parâmetros, pagina
        e formata o contexto.
        """
        page = request_params.get('page', 1)
        sort = request_params.get('sort', 'id')
        q = request_params.get('q', None)
        category = request_params.get('category', None)

        qs = self.get_base_queryset(sort=sort, q=q, category=category)
        paginator = Paginator(qs, self.paginate_by)
        page_obj = paginator.get_page(page)

        return {
            "wedding": self.wedding,
            "page_obj": page_obj,
            "items": page_obj.object_list,
            "current_sort": sort,
            "current_search": q or '',
            "current_category": category or '',
            "request": self.request
        }

    def render_item_list_response(self, request_params=None, trigger=None):
        """
        Renderiza a resposta HTMX APENAS da lista + paginação.
        Usado tanto por GET (filtro/paginação) quanto por POST (add/edit/delete).

        - Se 'request_params' for fornecido (GET), usa-o.
        - Se não (POST), lê o 'HX-Current-Url' para preservar o estado.
        """
        params = {}

        if request_params is not None:
            # Lógica para GET (Filtro, Paginação)
            params = request_params
        else:
            # Lógica para POST (Create, Update, Delete)
            # Lê o 'HX-Current-Url' para preservar o estado
            current_url = self.request.headers.get('Hx-Current-Url')
            if current_url:
                try:
                    query_string = urlparse(current_url).query
                    parsed_params = parse_qs(query_string)
                    params = {k: v[0] for k, v in parsed_params.items()}
                except Exception:
                    pass  # Se falhar, usa os defaults (page=1, etc)

        # Constrói o contexto com o estado correto
        context = self.build_paginated_context(params)

        # Renderiza o partial da lista + paginação (que faz OOB)
        html = render_to_string(
            "items/partials/_list_and_pagination.html",
            context,
            request=self.request,
        )

        response = HttpResponse(html)

        # Define o target principal. O partial fará OOB para a paginação.
        response["HX-Retarget"] = '#item-list-container'
        response["HX-Reswap"] = 'innerHTML'

        if trigger:
            response["HX-Trigger-After-Swap"] = trigger

        return response

    def render_full_tab_response(self, trigger=None):
        """
        Renderiza a resposta HTMX para Create/Update (POSTs de formulário).
        Retorna a ABA INTEIRA (item_list.html).
        Lê o 'HX-Current-Url' para preservar o estado de filtros/paginação
        que possa estar na URL do browser.
        """
        current_url = self.request.headers.get('Hx-Current-Url')
        params = {}
        if current_url:
            try:
                query_string = urlparse(current_url).query
                parsed_params = parse_qs(query_string)
                params = {k: v[0] for k, v in parsed_params.items()}
            except Exception:
                pass  # Usa defaults se falhar

        # Constrói o contexto com o estado correto
        context = self.build_paginated_context(params)

        # Renderiza o template da aba inteira
        html = render_to_string(
            "items/item_list.html",
            context,
            request=self.request,
        )

        response = HttpResponse(html)

        # IMPORTANTE: Não definimos HX-Retarget.
        # A resposta vai por defeito para o 'hx-target' do elemento
        # que iniciou o ciclo (o botão 'Adicionar Item'),
        # que era '#items-wrapper' com 'outerHTML'.
        # Como a nossa resposta também tem id="items-wrapper",
        # ela vai substituir o formulário perfeitamente.

        if trigger:
            response["HX-Trigger-After-Swap"] = trigger

        return response


class ItemFormLayoutMixin:
    """
    Define o layout e ícones para o formulário de Item.
    """
    form_class = ItemForm
    template_name = "items/partials/_item_form.html"

    # Você já tinha isso em AddItemView
    form_layout_dict = {
        "name": "col-6",
        "category": "col-md-6",
        # "status": "col-md-6",
        "quantity": "col-md-6",
        "unit_price": "col-md-6",
        "supplier": "col-12",
        "description": "col-12",
    }
    default_col_class = "col-12"
    form_icons = {
        "name": "fas fa-gift",
        "category": "fas fa-tags",
        # "status": "fas fa-check-circle",
        "quantity": "fas fa-hashtag",
        "unit_price": "fas fa-dollar-sign",
        "supplier": "fas fa-user-tie",
        "description": "fas fa-align-left",
    }

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["wedding"] = self.wedding
        ctx["form_layout_dict"] = self.form_layout_dict
        ctx["default_col_class"] = self.default_col_class
        ctx["form_icons"] = self.form_icons
        return ctx
