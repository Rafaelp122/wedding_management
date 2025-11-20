from unittest.mock import MagicMock, patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.views.generic import TemplateView, View

# Imports dos Mixins
from apps.items.mixins import (
    ItemFormLayoutMixin,
    ItemHtmxListResponseMixin,
    ItemListActionsMixin,
    ItemPaginationContextMixin,
    ItemQuerysetMixin,
    ItemWeddingContextMixin,
)
from apps.items.models import Item
from apps.users.models import User
from apps.weddings.models import Wedding


class ItemWeddingContextMixinTest(TestCase):
    """
    Testa a segurança e o carregamento de contexto (Gatekeeper).
    """
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("planner", "p@t.com", "123")
        cls.hacker = User.objects.create_user("hacker", "h@t.com", "123")

        cls.wedding = Wedding.objects.create(
            planner=cls.user, groom_name="G", bride_name="B",
            date="2025-01-01", location="Loc", budget=1000
        )

        cls.item = Item.objects.create(
            wedding=cls.wedding, name="Item", quantity=1, unit_price=10
        )

    def setUp(self):
        self.factory = RequestFactory()

        # View Dummy para testar o dispatch
        class DummyView(ItemWeddingContextMixin, View):
            def get(self, request, *args, **kwargs):
                return HttpResponse("OK")

        self.view_class = DummyView

    def test_load_by_wedding_id_success(self):
        """Deve carregar self.wedding se wedding_id for válido e usuário for dono."""
        request = self.factory.get("/")
        request.user = self.user

        view = self.view_class()
        view.setup(request, wedding_id=self.wedding.pk)
        view.dispatch(request)

        self.assertEqual(view.wedding, self.wedding)

    def test_load_by_wedding_id_forbidden_returns_404(self):
        """Se usuário não for dono do casamento, get_object_or_404 deve lançar 404."""
        request = self.factory.get("/")
        request.user = self.hacker  # Usuário errado

        view = self.view_class()
        view.setup(request, wedding_id=self.wedding.pk)

        # get_object_or_404 levanta Http404
        from django.http import Http404
        with self.assertRaises(Http404):
            view.dispatch(request)

    def test_load_by_item_pk_success(self):
        """Deve carregar self.wedding através do PK do item."""
        request = self.factory.get("/")
        request.user = self.user

        view = self.view_class()
        view.setup(request, pk=self.item.pk)
        view.dispatch(request)

        self.assertEqual(view.wedding, self.wedding)

    def test_load_by_item_pk_forbidden_returns_403(self):
        """Se o item existe mas é de outro planner, retorna 403."""
        request = self.factory.get("/")
        request.user = self.hacker

        view = self.view_class()
        view.setup(request, pk=self.item.pk)

        response = view.dispatch(request)
        self.assertEqual(response.status_code, 403)

    def test_load_by_item_pk_not_found_returns_404(self):
        """Se o item não existe, retorna 404."""
        request = self.factory.get("/")
        request.user = self.user

        view = self.view_class()
        view.setup(request, pk=99999)

        from django.http import Http404
        with self.assertRaises(Http404):
            view.dispatch(request)


class ItemQuerysetMixinTest(TestCase):
    """
    Testa a lógica de filtros da lista de itens.
    """
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("u", "u@t.com", "123")
        cls.wedding = Wedding.objects.create(
            planner=cls.user, groom_name="G", bride_name="B",
            date="2025-01-01", location="Loc", budget=1000
        )

        # Item do Casamento (Categoria A)
        cls.item1 = Item.objects.create(
            wedding=cls.wedding, name="Cadeira", category="DECOR",
            quantity=1, unit_price=10
        )
        # Item do Casamento (Categoria B)
        cls.item2 = Item.objects.create(
            wedding=cls.wedding, name="Mesa", category="LOCAL",
            quantity=1, unit_price=10
        )

        # Item de OUTRO Casamento (Não deve aparecer)
        other_w = Wedding.objects.create(
            planner=cls.user, groom_name="G2", bride_name="B2",
            date="2025-01-01", location="Loc", budget=1000
        )
        cls.item_other = Item.objects.create(
            wedding=other_w, name="Invasor", category="DECOR",
            quantity=1, unit_price=10
        )

    def setUp(self):
        # Mockamos uma view que já tem o self.wedding (simulando o ContextMixin)
        class QuerysetView(ItemQuerysetMixin):
            wedding = self.wedding
            request = None
        self.view = QuerysetView()

    def test_get_base_queryset_filters_by_wedding(self):
        """O queryset deve trazer apenas itens deste casamento."""
        qs = self.view.get_base_queryset()
        self.assertIn(self.item1, qs)
        self.assertIn(self.item2, qs)
        self.assertNotIn(self.item_other, qs)

    def test_get_base_queryset_filters_by_category(self):
        """Testa o filtro de categoria."""
        qs = self.view.get_base_queryset(category="DECOR")
        self.assertIn(self.item1, qs)
        self.assertNotIn(self.item2, qs)

    def test_get_base_queryset_search(self):
        """Testa a integração com a busca."""
        qs = self.view.get_base_queryset(q="Cadeira")
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first(), self.item1)


class ItemPaginationContextMixinTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("pg", "p@g.com", "123")
        cls.wedding = Wedding.objects.create(
            planner=cls.user, groom_name="G", bride_name="B",
            date="2025-01-01", location="L", budget=1000
        )

        # Cria 7 itens (paginate_by=6 -> 2 páginas)
        for i in range(7):
            Item.objects.create(
                wedding=cls.wedding, name=f"Item {i}",
                quantity=1, unit_price=10
            )

    def setUp(self):
        # Herdamos de Queryset e Pagination para integração
        class PaginatorView(ItemQuerysetMixin, ItemPaginationContextMixin):
            wedding = self.wedding
            request = RequestFactory().get("/")

        self.view = PaginatorView()

    def test_pagination_splits_pages(self):
        """Verifica se divide em páginas corretamente."""
        context = self.view.build_paginated_context({"page": 1})
        self.assertEqual(len(context["items"]), 6)
        self.assertTrue(context["page_obj"].has_next())

        context = self.view.build_paginated_context({"page": 2})
        self.assertEqual(len(context["items"]), 1)

    def test_context_vars_preserved(self):
        """Verifica se os filtros voltam no contexto (para persistir na UI)."""
        params = {"page": 1, "q": "busca", "category": "DECOR"}
        context = self.view.build_paginated_context(params)

        self.assertEqual(context["current_search"], "busca")
        self.assertEqual(context["current_category"], "DECOR")
        self.assertEqual(context["wedding"], self.wedding)


class ItemHtmxListResponseMixinTest(TestCase):
    def setUp(self):
        # View Dummy para testar o Mixin HTMX isoladamente
        class HtmxView(ItemHtmxListResponseMixin):
            # Mockamos o método de paginação pois já foi testado na outra classe
            # Aqui queremos testar apenas se os dados fluem de um método para o outro
            build_paginated_context = MagicMock(return_value={"context": "ok"})
            request = MagicMock()

        self.view = HtmxView()

    def test_get_htmx_context_data_bridges_params(self):
        """
        Verifica se os parâmetros extraídos do header HTMX são repassados
        para o construtor de contexto de paginação.
        """
        # Simulamos que o header trouxe ?page=2&category=DECOR
        mock_params = {"page": "2", "category": "DECOR"}

        # Mockamos o método que lê o header (HtmxUrlParamsMixin)
        with patch.object(self.view, '_get_params_from_htmx_url', return_value=mock_params):

            context = self.view.get_htmx_context_data()

            # Verifica se chamou a paginação com os params corretos
            self.view.build_paginated_context.assert_called_once_with(mock_params)

            # O método adiciona keys extras ao contexto retornado pelo
            # build_paginated_context
            expected_context = {
                "context": "ok",
                "pagination_url_name": "items:partial_items",
                "pagination_target": "#item-list-container",
                "pagination_aria_label": "Paginação de Itens",
            }
            self.assertEqual(context, expected_context)

    def test_render_item_list_response_defaults(self):
        """
        Verifica se o helper de renderização usa o trigger padrão 'listUpdated'.
        """
        with patch.object(self.view, 'render_htmx_response') as mock_render:
            self.view.render_item_list_response()

            # Deve chamar o render genérico passando o trigger correto
            mock_render.assert_called_once_with(trigger="listUpdated")

    def test_render_item_list_response_custom_trigger(self):
        """
        Verifica se aceita um trigger customizado.
        """
        with patch.object(self.view, 'render_htmx_response') as mock_render:
            self.view.render_item_list_response(trigger="itemDeleted")
            mock_render.assert_called_once_with(trigger="itemDeleted")


class ItemListActionsMixinTest(TestCase):
    def test_inheritance_structure(self):
        """
        Teste de Sanidade: Garante que a Fachada (Facade) herda
        das classes corretas para compor a funcionalidade completa.
        """
        from apps.items.mixins import ItemHtmxListResponseMixin, ItemQuerysetMixin

        self.assertTrue(issubclass(ItemListActionsMixin, ItemQuerysetMixin))
        self.assertTrue(issubclass(ItemListActionsMixin, ItemHtmxListResponseMixin))


class ItemFormLayoutMixinTest(TestCase):
    """
    Testa se o mixin de layout injeta as variáveis visuais corretamente.
    """
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("layout_user", "l@t.com", "123")
        cls.wedding = Wedding.objects.create(
            planner=cls.user, groom_name="G", bride_name="B",
            date="2025-01-01", location="Loc", budget=1000
        )

    def setUp(self):
        class DummyView(ItemFormLayoutMixin, TemplateView):
            wedding = self.wedding

        self.view = DummyView()
        self.view.request = RequestFactory().get("/")

    def test_context_data_contains_layout_vars(self):
        """
        O contexto deve conter o dicionário de layout, ícones e o objeto wedding.
        """
        context = self.view.get_context_data()

        # Verifica se o wedding foi repassado ao contexto (crucial para o template)
        self.assertEqual(context["wedding"], self.wedding)

        # Verifica variáveis de layout
        self.assertIn("form_layout_dict", context)
        self.assertIn("default_col_class", context)
        self.assertIn("form_icons", context)

        # Verifica integridade dos ícones (ex: ícone de 'name' deve ser 'fas fa-gift')
        self.assertEqual(context["form_icons"]["name"], "fas fa-gift")
        self.assertEqual(context["form_icons"]["unit_price"], "fas fa-dollar-sign")
