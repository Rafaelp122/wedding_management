from unittest.mock import patch

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.test import RequestFactory, SimpleTestCase

from apps.core.mixins.views import BaseHtmxResponseMixin, HtmxUrlParamsMixin

pytestmark = pytest.mark.unit


# Criamos uma View Dummy para herdar o Mixin e permitir o teste
class DummyView(HtmxUrlParamsMixin):
    pass


class HtmxUrlParamsMixinTest(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = DummyView()

    def test_no_htmx_header(self):
        """
        Deve retornar um dicionário vazio se o header Hx-Current-Url não existir.
        """
        request = self.factory.get("/")
        # RequestFactory não adiciona headers HTMX por padrão
        self.view.request = request

        params = self.view._get_params_from_htmx_url()
        self.assertEqual(params, {})

    def test_header_with_valid_params(self):
        """
        Deve extrair corretamente os parâmetros de uma URL válida no header.
        """
        url = "http://localhost:8000/lista?page=2&search=django&order=desc"
        request = self.factory.get("/", HTTP_HX_CURRENT_URL=url)
        self.view.request = request

        params = self.view._get_params_from_htmx_url()

        expected = {
            "page": "2",
            "search": "django",
            "order": "desc"
        }
        self.assertEqual(params, expected)

    def test_header_url_without_query_params(self):
        """
        Deve retornar vazio se a URL no header não tiver query string.
        """
        url = "http://localhost:8000/lista"
        request = self.factory.get("/", HTTP_HX_CURRENT_URL=url)
        self.view.request = request

        params = self.view._get_params_from_htmx_url()
        self.assertEqual(params, {})

    def test_duplicate_keys_takes_first_value(self):
        """
        Se houver chaves duplicadas (ex: ?a=1&a=2), seu código pega o v[0].
        """
        url = "http://localhost:8000/?tag=python&tag=javascript"
        request = self.factory.get("/", HTTP_HX_CURRENT_URL=url)
        self.view.request = request

        params = self.view._get_params_from_htmx_url()

        # O parse_qs retorna {'tag': ['python', 'javascript']}
        # Sua lógica faz v[0], então deve pegar 'python'
        self.assertEqual(params, {"tag": "python"})

    @patch("apps.core.mixins.views.urlparse")
    @patch("apps.core.mixins.views.logger")
    def test_exception_handling_logs_warning(self, mock_logger, mock_urlparse):
        """
        Deve capturar exceções, logar um aviso e retornar dict vazio sem quebrar.
        """
        # Simulamos um erro ao fazer o parse da URL
        mock_urlparse.side_effect = Exception("Erro simulado de parse")

        url = "http://invalid-url"
        request = self.factory.get("/", HTTP_HX_CURRENT_URL=url)
        self.view.request = request

        # Executa o método
        params = self.view._get_params_from_htmx_url()

        # Não deve quebrar (retorna dict vazio)
        self.assertEqual(params, {})

        # Deve ter chamado o logger.warning
        self.assertTrue(mock_logger.warning.called)

        # verificar a mensagem do log
        args, _ = mock_logger.warning.call_args
        self.assertIn("Falha ao parsear HX-Current-Url", args[0])

    def test_header_with_encoded_chars(self):
        """
        Testa se decodifica espaços e caracteres especiais (ex: 'a b' vira 'a b').
        """
        # "busca=são paulo" encodado
        url = "http://localhost:8000/lista?busca=s%C3%A3o%20paulo"
        request = self.factory.get("/", HTTP_HX_CURRENT_URL=url)
        self.view.request = request

        params = self.view._get_params_from_htmx_url()

        self.assertEqual(params, {"busca": "são paulo"})

    def test_header_with_empty_value(self):
        """
        Testa comportamento quando um parâmetro existe mas não tem valor (?page=).
        """
        url = "http://localhost:8000/lista?page=&filter=active"
        request = self.factory.get("/", HTTP_HX_CURRENT_URL=url)
        self.view.request = request

        params = self.view._get_params_from_htmx_url()

        # O parse_qs geralmente retorna string vazia para isso
        expected = {
            "page": "",
            "filter": "active"
        }
        self.assertEqual(params, expected)


class BaseHtmxResponseMixinTest(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        # Criamos uma classe dummy "on the fly" para testar o Mixin

        class ConcreteView(BaseHtmxResponseMixin):
            pass

        self.view = ConcreteView()
        self.view.request = self.factory.get("/")

    def test_improperly_configured_missing_template(self):
        """
        Deve lançar erro se htmx_template_name não for definido.
        """
        self.view.htmx_retarget_id = "#target"
        # htmx_template_name não foi definido

        with self.assertRaises(ImproperlyConfigured):
            self.view.render_htmx_response()

    def test_improperly_configured_missing_retarget(self):
        """
        Deve lançar erro se htmx_retarget_id não for definido.
        """
        self.view.htmx_template_name = "dummy.html"
        # htmx_retarget_id não foi definido

        with self.assertRaises(ImproperlyConfigured):
            self.view.render_htmx_response()

    @patch("apps.core.mixins.views.render_to_string")
    def test_render_response_headers_defaults(self, mock_render):
        """
        Deve renderizar o template e definir headers padrão (innerHTML).
        """
        # Configuração básica
        self.view.htmx_template_name = "template.html"
        self.view.htmx_retarget_id = "#my-target"

        # Mockamos o retorno do render_to_string para retornar um HTML falso
        mock_render.return_value = "<div>Conteúdo Renderizado</div>"

        response = self.view.render_htmx_response()

        # Verifica se o conteúdo do response é o que o render retornou
        self.assertEqual(response.content.decode(), "<div>Conteúdo Renderizado</div>")

        # Verifica os Headers HTMX Obrigatórios
        self.assertEqual(response["HX-Retarget"], "#my-target")
        self.assertEqual(response["HX-Reswap"], "innerHTML")  # Default

    @patch("apps.core.mixins.views.render_to_string")
    def test_render_response_custom_swap(self, mock_render):
        """
        Deve respeitar se mudarmos o htmx_reswap_method.
        """
        self.view.htmx_template_name = "template.html"
        self.view.htmx_retarget_id = "#target"
        self.view.htmx_reswap_method = "outerHTML"  # Mudando o padrão

        mock_render.return_value = "html"

        response = self.view.render_htmx_response()
        self.assertEqual(response["HX-Reswap"], "outerHTML")

    @patch("apps.core.mixins.views.render_to_string")
    def test_render_response_with_trigger(self, mock_render):
        """
        Deve adicionar o header HX-Trigger-After-Swap se o argumento for passado.
        """
        self.view.htmx_template_name = "template.html"
        self.view.htmx_retarget_id = "#target"
        mock_render.return_value = "html"

        # Chamamos passando um trigger
        response = self.view.render_htmx_response(trigger="updateList")

        self.assertEqual(response["HX-Trigger-After-Swap"], "updateList")

    @patch("apps.core.mixins.views.render_to_string")
    def test_context_data_passed_to_template(self, mock_render):
        """
        Verifica se os kwargs passados para render_htmx_response chegam
        ao template e se o 'request' é injetado automaticamente.
        """
        self.view.htmx_template_name = "template.html"
        self.view.htmx_retarget_id = "#target"
        mock_render.return_value = "html"

        # Passamos dados extras (ex: um form ou objeto)
        self.view.render_htmx_response(user_name="Rafael", age=30)

        # Verificamos como o mock foi chamado
        # render_to_string(template_name, context, request=...)
        args, kwargs = mock_render.call_args
        context_passed = args[1]  # O segundo argumento posicional é o context

        self.assertEqual(context_passed["user_name"], "Rafael")
        self.assertEqual(context_passed["age"], 30)
        self.assertEqual(context_passed["request"], self.view.request)

    def test_get_htmx_context_data_injects_request(self):
        """
        Verifica se o método get_htmx_context_data realmente adiciona
        o request e preserva os dados existentes.
        """
        # Dados de exemplo
        initial_data = {"usuario_id": 42, "status": "ativo"}

        # Chamamos o método diretamente (sem renderizar nada)
        context = self.view.get_htmx_context_data(**initial_data)

        # Verificações
        # O request deve ter sido adicionado
        self.assertIn("request", context)
        self.assertEqual(context["request"], self.view.request)

        # Os dados originais devem ter sido preservados
        self.assertEqual(context["usuario_id"], 42)
        self.assertEqual(context["status"], "ativo")
