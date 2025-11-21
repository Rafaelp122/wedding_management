"""
Testes para os mixins do app weddings.

Estes testes focam em comportamento e lógica de negócio crítica,
não em configuração estática ou detalhes de implementação.

Princípios seguidos:
- Testar comportamento, não implementação
- Testar lógica de negócio e segurança (ownership, filtros)
- Testar edge cases que podem causar bugs reais
"""
from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.test import RequestFactory, TestCase
from django.utils import timezone

from apps.users.models import User
from apps.weddings.mixins import (
    WeddingHtmxListResponseMixin,
    WeddingPaginationContextMixin,
    WeddingQuerysetMixin,
)
from apps.weddings.models import Wedding


class WeddingQuerysetMixinTest(TestCase):
    """
    Testes CRÍTICOS para WeddingQuerysetMixin.

    Foco: Segurança (isolamento de dados) e lógica de filtros.
    """

    @classmethod
    def setUpTestData(cls):
        """Dados para todos os testes."""
        cls.user = User.objects.create_user(
            username="planner", email="planner@test.com", password="123"
        )
        cls.other_user = User.objects.create_user(
            username="other", email="other@test.com", password="123"
        )

        # Data dinâmica para garantir status IN_PROGRESS
        future_date = timezone.now().date() + timedelta(days=365)

        # Casamento do planner (deve aparecer)
        cls.w1 = Wedding.objects.create(
            planner=cls.user,
            groom_name="G1",
            bride_name="B1",
            date=future_date,
            location="Loc",
            budget=1000,
        )

        # Casamento de outro usuário (NÃO deve aparecer)
        cls.w2 = Wedding.objects.create(
            planner=cls.other_user,
            groom_name="G2",
            bride_name="B2",
            date=future_date,
            location="Loc",
            budget=1000,
        )

    def setUp(self):
        """Configuração por teste."""
        class QuerysetView(WeddingQuerysetMixin):
            request = None

        self.view = QuerysetView()
        request = RequestFactory().get("/")
        request.user = self.user
        self.view.request = request

    def test_get_base_queryset_filters_by_user(self):
        """
        CRÍTICO (SEGURANÇA): Verifica isolamento de dados entre usuários.

        Cada planner só deve ver seus próprios casamentos.
        Falha aqui significa vazamento de dados entre usuários.
        """
        qs = self.view.get_base_queryset()

        self.assertIn(self.w1, qs)
        self.assertNotIn(self.w2, qs)

    def test_get_base_queryset_applies_search_filter(self):
        """
        IMPORTANTE: Verifica que busca funciona corretamente.

        Usuários dependem da busca para encontrar casamentos.
        """
        # Criar casamento com nome específico
        w3 = Wedding.objects.create(
            planner=self.user,
            groom_name="SearchMe",
            bride_name="B3",
            date="2025-01-01",
            location="Loc",
            budget=1000,
        )

        qs = self.view.get_base_queryset(q="SearchMe")

        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first(), w3)

    def test_get_base_queryset_filters_by_status(self):
        """
        IMPORTANTE: Verifica filtro de status (IN_PROGRESS/COMPLETED).

        Crucial para organização de casamentos do usuário.
        """
        # Criar casamento completado (data passada)
        w_completed = Wedding.objects.create(
            planner=self.user,
            groom_name="Old Groom",
            bride_name="Old Bride",
            date=timezone.now().date() - timedelta(days=10),
            location="Loc",
            budget=1000,
        )

        qs = self.view.get_base_queryset(status="COMPLETED")

        self.assertIn(w_completed, qs)
        self.assertNotIn(self.w1, qs)  # w1 é futuro (IN_PROGRESS)

    def test_get_base_queryset_has_annotations(self):
        """
        CRÍTICO: Verifica que anotações necessárias estão presentes.

        Templates dependem dessas anotações (items_count, progress, etc).
        Falha aqui causa erros no template.
        """
        qs = self.view.get_base_queryset()
        wedding = qs.first()

        # Estas anotações são CRÍTICAS para o template
        self.assertTrue(hasattr(wedding, 'items_count'))
        self.assertTrue(hasattr(wedding, 'contracts_count'))
        self.assertTrue(hasattr(wedding, 'effective_status'))
        self.assertTrue(hasattr(wedding, 'progress'))


class WeddingPaginationContextMixinTest(TestCase):
    """
    Testes para WeddingPaginationContextMixin.

    Foco: Paginação correta e preservação de filtros.
    """

    @classmethod
    def setUpTestData(cls):
        """Dados para todos os testes."""
        cls.user = User.objects.create_user(
            username="paginator_user",
            email="paginator@test.com",
            password="123"
        )

        # Criar 7 casamentos para testar paginação (paginate_by=6)
        for i in range(7):
            Wedding.objects.create(
                planner=cls.user,
                groom_name=f"Groom {i}",
                bride_name=f"Bride {i}",
                date="2025-01-01",
                location="Loc",
                budget=1000,
            )

    def setUp(self):
        """Configuração por teste."""
        # View que herda Queryset + Pagination para testar integração
        class ConcretePaginationView(
            WeddingQuerysetMixin, WeddingPaginationContextMixin
        ):
            pass

        self.view = ConcretePaginationView()
        request = RequestFactory().get("/")
        request.user = self.user
        self.view.request = request

    def test_pagination_splits_records(self):
        """
        CRÍTICO: Verifica que paginação divide registros corretamente.

        Com 7 registros e paginate_by=6, deve criar 2 páginas.
        """
        # Página 1
        context = self.view.build_paginated_context({"page": 1})

        self.assertEqual(len(context["paginated_weddings"]), 6)
        self.assertTrue(context["page_obj"].has_next())

        # Página 2
        context = self.view.build_paginated_context({"page": 2})

        self.assertEqual(len(context["paginated_weddings"]), 1)
        self.assertFalse(context["page_obj"].has_next())

    def test_filters_are_preserved_in_pagination(self):
        """
        CRÍTICO: Verifica que filtros são preservados ao navegar páginas.

        Usuário não pode perder busca/filtros ao mudar de página.
        """
        # Criar casamento específico para buscar
        Wedding.objects.create(
            planner=self.user,
            groom_name="TargetUnique",
            bride_name="B",
            date="2025-01-01",
            location="L",
            budget=1000,
        )

        # Paginar com filtro de busca
        params = {"page": 1, "q": "TargetUnique"}
        context = self.view.build_paginated_context(params)

        # Deve retornar APENAS o item buscado
        self.assertEqual(len(context["paginated_weddings"]), 1)
        self.assertEqual(
            context["paginated_weddings"][0]["wedding"].groom_name,
            "TargetUnique"
        )

        # Contexto deve devolver termo de busca (para template persistir)
        self.assertEqual(context["current_search"], "TargetUnique")

    def test_pagination_handles_invalid_page_param(self):
        """
        IMPORTANTE: Edge case - página inválida não deve quebrar.

        Previne erro 500 em produção com ?page=banana ou ?page=999
        """
        # Caso 1: Texto inválido (?page=banana)
        context = self.view.build_paginated_context({"page": "banana"})
        # Default para página 1
        self.assertEqual(context["page_obj"].number, 1)

        # Caso 2: Número fora do limite (?page=999)
        context = self.view.build_paginated_context({"page": 999})
        self.assertEqual(context["page_obj"].number, 2)  # Última página


class WeddingHtmxListResponseMixinTest(TestCase):
    """
    Testes para WeddingHtmxListResponseMixin.

    Foco: Integração entre parâmetros HTMX e contexto.
    """

    def setUp(self):
        """Configuração por teste."""
        class HtmxView(WeddingHtmxListResponseMixin):
            # Mock do método de construir contexto
            build_paginated_context = MagicMock(return_value={"mock": "data"})
            request = MagicMock()

        self.view = HtmxView()

    def test_get_htmx_context_data_bridges_params(self):
        """
        IMPORTANTE: Verifica que parâmetros do HTMX são passados corretamente.

        Frontend HTMX envia parâmetros no header que devem ser
        extraídos e usados para paginação/filtros.
        """
        # Mock do retorno de parâmetros HTMX
        expected_params = {"page": "2", "q": "teste"}

        with patch.object(
            self.view, "_get_params_from_htmx_url",
            return_value=expected_params
        ):
            context = self.view.get_htmx_context_data()

            # Verifica que método de paginação foi chamado com params corretos
            self.view.build_paginated_context.assert_called_once_with(
                expected_params
            )

            # Verifica que retornou o contexto correto
            self.assertEqual(context, {"mock": "data"})
