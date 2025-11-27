from datetime import date
from unittest.mock import MagicMock

import pytest
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.exceptions import ImproperlyConfigured
from django.test import RequestFactory, SimpleTestCase, TestCase
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView

from apps.core.mixins.auth import OwnerRequiredMixin, RedirectAuthenticatedUserMixin
from apps.users.models import User
from apps.weddings.models import Wedding


@pytest.mark.unit
class OwnerRequiredMixinTest(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

        # Criamos uma view dummy para testar
        class ConcreteView(OwnerRequiredMixin):
            pass

        self.view = ConcreteView()

        # Simulamos um usuário logado (não precisa ser salvo no BD para esse teste)
        self.user = User(username="tester", id=1)
        request = self.factory.get("/")
        request.user = self.user
        self.view.request = request

    def test_improperly_configured_missing_model(self):
        """
        Deve lançar erro se a view não tiver o atributo 'model'.
        """
        self.view.owner_field_name = "user"
        # model não definido

        with self.assertRaises(ImproperlyConfigured) as cm:
            self.view.get_queryset()

        self.assertIn("must define a 'model'", str(cm.exception))

    def test_improperly_configured_missing_owner_field(self):
        """
        Deve lançar erro se a view não tiver 'owner_field_name'.
        """
        self.view.model = MagicMock()  # Simulamos um model qualquer
        # owner_field_name não definido (é None por padrão no Mixin)

        with self.assertRaises(ImproperlyConfigured) as cm:
            self.view.get_queryset()

        self.assertIn("must define 'owner_field_name'", str(cm.exception))

    def test_get_queryset_filters_by_owner(self):
        """
        Deve chamar o filter do queryset com o campo e usuário corretos.
        """
        # Configuração
        self.view.owner_field_name = "criador"

        # Mockando o Model e o Manager (objects)
        mock_model = MagicMock()
        mock_queryset = MagicMock()

        # Quando chamar model.objects.all(), retorna nosso mock_queryset
        mock_model.objects.all.return_value = mock_queryset

        # Quando chamar mock_queryset.filter(...), retorna ele mesmo (chaining)
        mock_queryset.filter.return_value = mock_queryset

        self.view.model = mock_model

        # EXECUÇÃO
        result = self.view.get_queryset()

        # VERIFICAÇÃO
        # Verifica se chamou .all()
        mock_model.objects.all.assert_called_once()

        # Verifica se chamou .filter(criador=self.user)
        mock_queryset.filter.assert_called_once_with(criador=self.user)

        # O retorno deve ser o queryset filtrado
        self.assertEqual(result, mock_queryset)

    def test_login_required_inheritance(self):
        """
        Garante que o mixin herda de LoginRequiredMixin.
        (Teste estrutural simples)
        """
        from django.contrib.auth.mixins import LoginRequiredMixin

        self.assertTrue(issubclass(OwnerRequiredMixin, LoginRequiredMixin))


@pytest.mark.integration
class OwnerRequiredMixinIntegrationTest(TestCase):
    """
    Teste de Integração usando os Models reais (User e Wedding).
    Verifica se o filtro SQL realmente isola os dados entre planners.
    """

    @classmethod
    def setUpTestData(cls):
        # Criamos dois Planners (Usuários) diferentes
        cls.planner_alpha = User.objects.create_user(
            username="alpha", email="alpha@test.com", password="123"
        )
        cls.planner_beta = User.objects.create_user(
            username="beta", email="beta@test.com", password="123"
        )

        # Criamos Casamentos para o Planner Alpha
        cls.wedding_alpha = Wedding.objects.create(
            planner=cls.planner_alpha,
            groom_name="Alpha Groom",
            bride_name="Alpha Bride",
            date=date(2025, 12, 25),
            location="Rio de Janeiro",
            budget=50000.00,
        )

        # Criamos Casamentos para o Planner Beta
        cls.wedding_beta = Wedding.objects.create(
            planner=cls.planner_beta,
            groom_name="Beta Groom",
            bride_name="Beta Bride",
            date=date(2026, 1, 1),
            location="São Paulo",
            budget=100000.00,
        )

    def setUp(self):
        # Configura uma View Concreta usando seus models reais
        class WeddingListView(OwnerRequiredMixin, ListView):
            model = Wedding
            owner_field_name = "planner"

        self.view = WeddingListView()
        self.factory = (
            RequestFactory()
        )  # Certifique-se de importar RequestFactory lá em cima

    def test_planner_alpha_sees_only_his_weddings(self):
        """
        Se eu sou o Planner Alpha, o get_queryset SÓ pode trazer o
        wedding_alpha.
        """
        # Simulamos requisição do Alpha
        request = self.factory.get("/")
        request.user = self.planner_alpha
        self.view.request = request

        queryset = self.view.get_queryset()

        # O Casamento do Alpha DEVE estar lá
        self.assertTrue(queryset.filter(pk=self.wedding_alpha.pk).exists())

        # O Casamento do Beta NÃO pode estar lá
        self.assertFalse(queryset.filter(pk=self.wedding_beta.pk).exists())

    def test_planner_beta_sees_only_his_weddings(self):
        """
        Se eu sou o Planner Beta, o get_queryset SÓ pode trazer o wedding_beta.
        """
        # Simulamos requisição do Beta
        request = self.factory.get("/")
        request.user = self.planner_beta
        self.view.request = request

        queryset = self.view.get_queryset()

        # O Casamento do Beta DEVE estar lá
        self.assertTrue(queryset.filter(pk=self.wedding_beta.pk).exists())

        # O Casamento do Alpha NÃO pode estar lá
        self.assertFalse(queryset.filter(pk=self.wedding_alpha.pk).exists())

    def test_anonymous_user_is_redirected(self):
        """
        Garante que o LoginRequiredMixin está funcionando:
        Usuário anônimo nem chega a tocar no get_queryset,
        é redirecionado antes.
        """
        # Criamos um request anônimo
        request = self.factory.get("/")
        request.user = AnonymousUser()

        # Precisamos simular o fluxo de entrada da View (dispatch)
        # para ativar a proteção do LoginRequiredMixin

        # Instanciamos a view novamente para esse teste específico
        view = self.view.__class__()  # Cria nova instância da classe da view
        view.setup(request)  # Configura o request básico

        # O dispatch é quem checa o login
        response = view.dispatch(request)

        # Deve redirecionar (Status 302) para a página de login
        self.assertEqual(response.status_code, 302)
        # Opcional: verificar se vai para /accounts/login/ (depende da sua config)
        self.assertIn("login", response.url)

    def test_user_with_no_weddings_gets_empty_list(self):
        """
        Usuário logado, mas sem casamentos, não deve gerar erro.
        Deve apenas retornar uma lista vazia.
        """
        # Criamos um usuário novo (Charlie) que não tem casamentos no setUpTestData
        user_charlie = User.objects.create_user(
            username="charlie", email="charlie@test.com", password="123"
        )

        request = self.factory.get("/")
        request.user = user_charlie
        self.view.request = request

        queryset = self.view.get_queryset()

        # Não deve ser None, deve ser um QuerySet vazio
        self.assertFalse(queryset.exists())
        self.assertEqual(queryset.count(), 0)


@pytest.mark.unit
class RedirectAuthenticatedUserMixinTest(SimpleTestCase):
    """
    Testes Unitários Puros (sem banco de dados).
    Simulamos o usuário com Mocks.
    """

    def setUp(self):
        self.factory = RequestFactory()

        class PublicView(RedirectAuthenticatedUserMixin, TemplateView):
            template_name = "dummy.html"

        self.view_class = PublicView

    def _setup_request(self, user):
        """Helper para configurar request com mensagens"""
        request = self.factory.get("/login")
        request.user = user

        # Configura mensagens sem banco de dados
        request.session = "session"
        messages = FallbackStorage(request)
        request._messages = messages
        return request

    def test_anonymous_user_can_access_view(self):
        # AnonymousUser já é um objeto em memória, não toca no banco
        request = self._setup_request(AnonymousUser())

        view = self.view_class()
        view.setup(request)
        response = view.dispatch(request)

        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_is_redirected(self):
        # MOCK: Fingimos um usuário logado
        mock_user = MagicMock()
        mock_user.is_authenticated = True
        mock_user.first_name = "Teste"
        mock_user.username = "teste_user"

        request = self._setup_request(mock_user)

        view = self.view_class()
        view.setup(request)
        response = view.dispatch(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse_lazy("weddings:my_weddings"))

    def test_redirect_message_uses_first_name(self):
        # MOCK: Usuário com first_name
        mock_user = MagicMock()
        mock_user.is_authenticated = True
        mock_user.first_name = "João"
        mock_user.username = "joao123"

        request = self._setup_request(mock_user)

        view = self.view_class()
        view.setup(request)
        view.dispatch(request)

        # Verificamos a mensagem diretamente no storage
        messages = list(request._messages)
        self.assertEqual(str(messages[0]), "Bem vindo de volta, João!")

    def test_redirect_message_fallback_to_username(self):
        # MOCK: Usuário SEM first_name (string vazia ou None)
        mock_user = MagicMock()
        mock_user.is_authenticated = True
        mock_user.first_name = ""
        mock_user.username = "usuario_sem_nome"

        request = self._setup_request(mock_user)

        view = self.view_class()
        view.setup(request)
        view.dispatch(request)

        messages = list(request._messages)
        self.assertEqual(str(messages[0]), "Bem vindo de volta, usuario_sem_nome!")
