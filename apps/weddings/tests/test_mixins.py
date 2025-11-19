from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.test import RequestFactory, TestCase
from django.utils import timezone
from django.views.generic import DetailView

from apps.core.constants import GRADIENTS
from apps.users.models import User

# Imports dos seus Mixins
from apps.weddings.mixins import (
    PlannerOwnershipMixin,
    WeddingFormLayoutMixin,
    WeddingHtmxListResponseMixin,
    WeddingListActionsMixin,
    WeddingPaginationContextMixin,
    WeddingQuerysetMixin,
)
from apps.weddings.models import Wedding


class PlannerOwnershipMixinTest(TestCase):
    def test_configuration(self):
        """
        Verifica se o mixin está configurado com o Model e Campo corretos.
        """
        mixin = PlannerOwnershipMixin()
        self.assertEqual(mixin.model, Wedding)
        self.assertEqual(mixin.owner_field_name, "planner")


class WeddingFormLayoutMixinTest(TestCase):
    def setUp(self):
        # Criamos uma view dummy para testar o contexto
        class DummyView(WeddingFormLayoutMixin, DetailView):
            object = None  # Necessário para DetailView não reclamar

        self.view = DummyView()
        self.view.request = RequestFactory().get("/")

    def test_context_data_contains_layout_vars(self):
        """
        Verifica se o get_context_data injeta os dicionários de layout.
        """
        context = self.view.get_context_data()

        self.assertIn("form_layout_dict", context)
        self.assertIn("default_col_class", context)
        self.assertIn("form_icons", context)

        # Verifica um valor específico para garantir integridade
        self.assertEqual(context["form_icons"]["budget"], "fas fa-money-bill-wave")


class WeddingQuerysetMixinTest(TestCase):
    """
    Testa a lógica de construção do Queryset isolada da View.
    """
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="planner",
            email="planner@test.com",
            password="123"
        )
        cls.other_user = User.objects.create_user(
            username="other",
            email="other@test.com",
            password="123"
        )

        # DATA FUTURA DINÂMICA (Hoje + 1 ano)
        # Isso garante que este casamento sempre será IN_PROGRESS
        future_date = timezone.now().date() + timedelta(days=365)

        # Casamento do Planner (deve aparecer)
        cls.w1 = Wedding.objects.create(
            planner=cls.user,
            groom_name="G1", bride_name="B1",
            date=future_date, location="Loc", budget=1000
        )
        # Casamento de Outro (não deve aparecer)
        cls.w2 = Wedding.objects.create(
            planner=cls.other_user,
            groom_name="G2", bride_name="B2",
            date=future_date, location="Loc", budget=1000
        )

    def setUp(self):
        # View Dummy apenas com o Mixin de Queryset
        class QuerysetView(WeddingQuerysetMixin):
            request = None

        self.view = QuerysetView()
        request = RequestFactory().get("/")
        request.user = self.user
        self.view.request = request

    def test_get_base_queryset_filters_by_user(self):
        """
        Garante que o get_base_queryset filtra pelo request.user.
        """
        qs = self.view.get_base_queryset()

        self.assertIn(self.w1, qs)
        self.assertNotIn(self.w2, qs)

    def test_get_base_queryset_applies_filters_and_sort(self):
        """
        Garante que os parâmetros (sort, q, status) são repassados.
        """
        # Cria mais um casamento para testar filtro
        w3 = Wedding.objects.create(
            planner=self.user,
            groom_name="SearchMe", bride_name="B3",
            date="2025-01-01", location="Loc", budget=1000
        )

        # Testando filtro de busca (q)
        qs = self.view.get_base_queryset(q="SearchMe")
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first(), w3)

    def test_get_base_queryset_filters_by_status(self):
        """
        Testa se o filtro de status está funcionando.
        """
        from datetime import timedelta

        from django.utils import timezone

        # self.w1 existe AQUI nesta classe

        w_completed = Wedding.objects.create(
            planner=self.user,
            groom_name="Old Groom", bride_name="Old Bride",
            date=timezone.now().date() - timedelta(days=10),
            location="Loc", budget=1000
        )

        qs = self.view.get_base_queryset(status="COMPLETED")

        self.assertIn(w_completed, qs)
        self.assertNotIn(self.w1, qs)


# --- Teste de Paginação e Contexto ---

class WeddingPaginationContextMixinTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # CORREÇÃO: Adicionando o email obrigatório
        cls.user = User.objects.create_user(
            username="paginator_user",
            email="paginator@test.com",
            password="123"
        )

        # Criamos 7 casamentos para testar paginação (Paginate by 6)
        for i in range(7):
            Wedding.objects.create(
                planner=cls.user,
                groom_name=f"Groom {i}", bride_name=f"Bride {i}",
                date="2025-01-01", location="Loc", budget=1000
            )

    def setUp(self):
        # Criamos uma View que herda de Queryset E Pagination para testar a integração
        from apps.weddings.mixins import WeddingQuerysetMixin

        class ConcretePaginationView(WeddingQuerysetMixin, WeddingPaginationContextMixin):
            pass

        self.view = ConcretePaginationView()
        request = RequestFactory().get("/")
        request.user = self.user
        self.view.request = request

    def test_pagination_splits_records(self):
        """
        Com 7 registros e paginate_by=6, deve criar 2 páginas.
        """
        # Pede a página 1
        context = self.view.build_paginated_context({"page": 1})
        self.assertEqual(len(context["paginated_weddings"]), 6)
        self.assertTrue(context["page_obj"].has_next())

        # Pede a página 2
        context = self.view.build_paginated_context({"page": 2})
        self.assertEqual(len(context["paginated_weddings"]), 1)
        self.assertFalse(context["page_obj"].has_next())

    def test_gradients_cycling_logic(self):
        """
        Verifica se os gradientes são atribuídos ciclicamente.
        """
        # Vamos pegar a página 1 com 6 itens
        context = self.view.build_paginated_context({"page": 1})
        items = context["paginated_weddings"]

        # Total de gradientes disponíveis
        total_gradients = len(GRADIENTS)

        # Verifica o item 0
        self.assertEqual(items[0]["gradient"], GRADIENTS[0])

        # Se tivermos mais itens que gradientes, deve fazer o loop (modulo)
        # Ex: Se temos 5 gradientes, o item índice 5 (sexto item) deve ser o gradiente 0
        if len(items) > total_gradients:
            self.assertEqual(items[total_gradients]["gradient"], GRADIENTS[0])

    def test_filters_are_preserved_in_pagination(self):
        """
        Garante que filtros (q, sort) passados nos params afetam o resultado paginado.
        """
        # Cria um registro específico para buscar
        Wedding.objects.create(
            planner=self.user, 
            groom_name="TargetUnique", bride_name="B", 
            date="2025-01-01", location="L", budget=1000
        )

        # Pagina com filtro de busca
        params = {"page": 1, "q": "TargetUnique"}
        context = self.view.build_paginated_context(params)

        # Deve retornar APENAS o item buscado, ignorando os outros 7
        self.assertEqual(len(context["paginated_weddings"]), 1)
        self.assertEqual(context["paginated_weddings"][0]["wedding"].groom_name, "TargetUnique")

        # Verifica se o contexto final devolve o termo de busca (para o template persistir)
        self.assertEqual(context["current_search"], "TargetUnique")

    def test_pagination_handles_invalid_page_param(self):
        """
        Garante que o mixin não quebra se o parâmetro 'page' for inválido.
        O comportamento esperado do get_page() é:
        - Texto/Inválido -> Retorna página 1
        - Fora de alcance -> Retorna última página
        """
        # Caso 1: Texto inválido (?page=banana)
        context = self.view.build_paginated_context({"page": "banana"})
        self.assertEqual(context["page_obj"].number, 1)

        # Caso 2: Número fora do limite (?page=999)
        # Como temos 7 itens e paginate_by=6, temos 2 páginas.
        context = self.view.build_paginated_context({"page": 999})
        self.assertEqual(context["page_obj"].number, 2)  # Última página


# --- Teste de Integração HTMX ---

class WeddingHtmxListResponseMixinTest(TestCase):
    def setUp(self):
        # View completa simulada
        class HtmxView(WeddingHtmxListResponseMixin):
            # Mockamos o método de construir contexto para não depender do banco/pagination real
            # Queremos testar apenas a "Ponte" do HTMX
            build_paginated_context = MagicMock(return_value={"mock": "data"})
            request = MagicMock()

        self.view = HtmxView()

    def test_get_htmx_context_data_bridges_params(self):
        """
        Testa se os parâmetros extraídos do header HTMX são passados
        corretamente para o build_paginated_context.
        """
        # 1. Mockamos o retorno do params do HTMX (simulando o Mixin HtmxUrlParamsMixin)
        # Dizemos que a URL no header tinha ?page=2&q=teste
        expected_params = {"page": "2", "q": "teste"}

        with patch.object(self.view, '_get_params_from_htmx_url', return_value=expected_params):

            # 2. Chama o método
            context = self.view.get_htmx_context_data()

            # 3. Verifica se o método de paginação foi chamado com os params que vieram do header
            self.view.build_paginated_context.assert_called_once_with(expected_params)

            # 4. Verifica se retornou o que o build_paginated_context devolveu
            self.assertEqual(context, {"mock": "data"})

    def test_render_wedding_list_response_defaults(self):
        """
        Testa se o render chama o render_htmx_response com os triggers corretos.
        """
        # Mock do render_htmx_response (que vem do BaseHtmxResponseMixin)
        with patch.object(self.view, 'render_htmx_response') as mock_render:

            self.view.render_wedding_list_response()

            # Deve chamar com o trigger default
            mock_render.assert_called_once_with(trigger="listUpdated")

    def test_render_wedding_list_response_custom_trigger(self):
        """
        Testa se é possível sobrescrever o trigger padrão.
        """
        with patch.object(self.view, 'render_htmx_response') as mock_render:

            self.view.render_wedding_list_response(trigger="SpecialEvent")

            mock_render.assert_called_once_with(trigger="SpecialEvent")


# --- Teste de Facade (Herança) ---

class WeddingListActionsMixinTest(TestCase):
    def test_inheritance_structure(self):
        """
        Testa se o mixin de fachada herda das classes corretas.
        """
        from apps.weddings.mixins import (
            WeddingHtmxListResponseMixin,
            WeddingQuerysetMixin,
        )

        # Verifica MRO (Method Resolution Order) ou issubclass
        self.assertTrue(issubclass(WeddingListActionsMixin, WeddingQuerysetMixin))
        self.assertTrue(issubclass(WeddingListActionsMixin, WeddingHtmxListResponseMixin))
