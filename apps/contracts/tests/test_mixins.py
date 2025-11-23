"""
Testes para os mixins do app contracts.
"""
from unittest.mock import Mock, patch

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.test import RequestFactory, TestCase

from apps.contracts.mixins import (ClientIPMixin, ContractOwnershipMixin,
                                   PDFResponseMixin, TokenAccessMixin)
from apps.contracts.models import Contract
from apps.items.models import Item
from apps.users.models import User
from apps.weddings.models import Wedding


class ClientIPMixinTest(TestCase):
    """Testes para o ClientIPMixin."""

    def setUp(self):
        self.factory = RequestFactory()
        self.mixin = ClientIPMixin()

    def test_get_client_ip_from_remote_addr(self):
        """Deve extrair IP do REMOTE_ADDR quando não há proxy."""
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '192.168.1.100'
        self.mixin.request = request

        ip = self.mixin.get_client_ip()

        self.assertEqual(ip, '192.168.1.100')

    def test_get_client_ip_from_x_forwarded_for(self):
        """Deve pegar o primeiro IP do X-Forwarded-For."""
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '203.0.113.1, 198.51.100.1'
        request.META['REMOTE_ADDR'] = '10.0.0.1'
        self.mixin.request = request

        ip = self.mixin.get_client_ip()

        # Deve pegar o primeiro (cliente original)
        self.assertEqual(ip, '203.0.113.1')

    def test_get_client_ip_strips_whitespace(self):
        """Deve remover espaços em branco do IP."""
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '  192.168.1.1  , 10.0.0.1'
        self.mixin.request = request

        ip = self.mixin.get_client_ip()

        self.assertEqual(ip, '192.168.1.1')

    def test_get_client_ip_returns_unknown_when_missing(self):
        """Deve retornar 'unknown' quando não há informação de IP."""
        request = self.factory.get("/")
        # Remove REMOTE_ADDR completamente
        del request.META['REMOTE_ADDR']
        # Sem REMOTE_ADDR e sem X-Forwarded-For
        self.mixin.request = request

        ip = self.mixin.get_client_ip()

        self.assertEqual(ip, 'unknown')


class ContractOwnershipMixinTest(TestCase):
    """Testes para o ContractOwnershipMixin."""

    def setUp(self):
        self.factory = RequestFactory()
        self.mixin = ContractOwnershipMixin()

        # Cria usuários e dados de teste
        self.owner = User.objects.create_user(
            'owner', 'owner@test.com', '123'
        )
        self.other_user = User.objects.create_user(
            'other', 'other@test.com', '123'
        )

        self.wedding = Wedding.objects.create(
            planner=self.owner,
            groom_name="João",
            bride_name="Maria",
            date="2025-06-15",
            location="Salão",
            budget=50000
        )

        self.item = Item.objects.create(
            wedding=self.wedding,
            name="Fotógrafo",
            quantity=1,
            unit_price=5000
        )

        self.contract = Contract.objects.create(item=self.item)

    def test_get_contract_or_403_success_for_owner(self):
        """Proprietário deve conseguir acessar o contrato."""
        request = self.factory.get('/')
        request.user = self.owner
        self.mixin.request = request

        contract = self.mixin.get_contract_or_403(self.contract.id)

        self.assertEqual(contract, self.contract)

    def test_get_contract_or_403_raises_for_other_user(self):
        """Outro usuário deve receber PermissionDenied."""
        request = self.factory.get('/')
        request.user = self.other_user
        self.mixin.request = request

        with self.assertRaises(PermissionDenied):
            self.mixin.get_contract_or_403(self.contract.id)

    def test_get_contract_or_403_raises_for_anonymous(self):
        """Usuário anônimo deve ser bloqueado."""
        request = self.factory.get('/')
        request.user = AnonymousUser()
        self.mixin.request = request

        with self.assertRaises(PermissionDenied):
            self.mixin.get_contract_or_403(self.contract.id)

    def test_get_contract_or_403_returns_404_for_invalid_id(self):
        """ID inválido deve retornar 404."""
        from django.http import Http404

        request = self.factory.get('/')
        request.user = self.owner
        self.mixin.request = request

        with self.assertRaises(Http404):
            self.mixin.get_contract_or_403(99999)


class TokenAccessMixinTest(TestCase):
    """Testes para o TokenAccessMixin."""

    def setUp(self):
        self.mixin = TokenAccessMixin()

        # Cria contrato com token
        user = User.objects.create_user('user', 'u@test.com', '123')
        wedding = Wedding.objects.create(
            planner=user,
            groom_name="Pedro",
            bride_name="Ana",
            date="2025-12-01",
            location="Igreja",
            budget=30000
        )
        item = Item.objects.create(
            wedding=wedding,
            name="DJ",
            quantity=1,
            unit_price=2000
        )
        self.contract = Contract.objects.create(item=item)

    def test_get_contract_by_token_success(self):
        """Deve retornar contrato com token válido."""
        self.mixin.kwargs = {"token": self.contract.token}

        contract = self.mixin.get_contract_by_token()

        self.assertEqual(contract, self.contract)

    def test_get_contract_by_token_raises_404_for_invalid_token(self):
        """Token inválido deve retornar 404."""
        import uuid

        from django.http import Http404

        self.mixin.kwargs = {"token": uuid.uuid4()}

        with self.assertRaises(Http404):
            self.mixin.get_contract_by_token()


class PDFResponseMixinTest(TestCase):
    """Testes para o PDFResponseMixin."""

    def setUp(self):
        self.factory = RequestFactory()
        self.mixin = PDFResponseMixin()
        self.mixin.request = self.factory.get('/')

    def test_render_to_pdf_returns_http_response(self):
        """Deve retornar HttpResponse com PDF."""
        self.mixin.pdf_template_name = 'contracts/pdf_template.html'

        # Mock do template e pisa
        with patch('apps.contracts.mixins.get_template') as mock_get_template:
            mock_template = Mock()
            mock_template.render.return_value = '<html>Test</html>'
            mock_get_template.return_value = mock_template

            with patch('apps.contracts.mixins.pisa.CreatePDF') as mock_pisa:
                mock_pisa.return_value.err = False

                response = self.mixin.render_to_pdf(
                    context={'test': 'data'},
                    filename='test.pdf'
                )

        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('test.pdf', response['Content-Disposition'])

    def test_render_to_pdf_uses_template_name_parameter(self):
        """Deve usar template_name passado como parâmetro."""
        with patch('apps.contracts.mixins.get_template') as mock_get_template:
            mock_template = Mock()
            mock_template.render.return_value = '<html>Custom</html>'
            mock_get_template.return_value = mock_template

            with patch('apps.contracts.mixins.pisa.CreatePDF') as mock_pisa:
                mock_pisa.return_value.err = False

                self.mixin.render_to_pdf(
                    context={},
                    filename='custom.pdf',
                    template_name='custom/template.html'
                )

            # Verifica se usou o template correto
            mock_get_template.assert_called_once_with('custom/template.html')

    def test_render_to_pdf_returns_error_when_no_template(self):
        """Deve retornar erro 500 se não houver template configurado."""
        # Não define pdf_template_name
        response = self.mixin.render_to_pdf(
            context={},
            filename='test.pdf'
        )

        self.assertEqual(response.status_code, 500)
        self.assertIn('Configuração', response.content.decode())

    def test_render_to_pdf_returns_error_when_pisa_fails(self):
        """Deve retornar erro 500 se pisa falhar."""
        self.mixin.pdf_template_name = 'contracts/pdf_template.html'

        with patch('apps.contracts.mixins.get_template') as mock_get_template:
            mock_template = Mock()
            mock_template.render.return_value = '<html>Bad</html>'
            mock_get_template.return_value = mock_template

            with patch('apps.contracts.mixins.pisa.CreatePDF') as mock_pisa:
                mock_pisa.return_value.err = True  # Simula erro

                response = self.mixin.render_to_pdf(
                    context={},
                    filename='test.pdf'
                )

        self.assertEqual(response.status_code, 500)
        self.assertIn('Erro ao gerar PDF', response.content.decode())

    def test_pdf_link_callback_resolves_static_files(self):
        """Link callback deve resolver arquivos estáticos."""
        import os

        from django.conf import settings

        # Simula um arquivo que existe
        test_path = os.path.join(
            settings.STATIC_ROOT or '/static',
            'test.css'
        )

        with patch('os.path.isfile', return_value=True):
            result = self.mixin._pdf_link_callback(
                f"{settings.STATIC_URL}test.css",
                ""
            )

        # Deve retornar o caminho absoluto
        self.assertTrue(result.endswith('test.css'))

    def test_pdf_link_callback_returns_uri_for_nonexistent_file(self):
        """Link callback deve retornar URI original se arquivo não existir."""
        from django.conf import settings

        with patch('os.path.isfile', return_value=False):
            result = self.mixin._pdf_link_callback(
                f"{settings.STATIC_URL}nonexistent.css",
                ""
            )

        # Deve retornar a URI original
        self.assertEqual(result, f"{settings.STATIC_URL}nonexistent.css")

    def test_pdf_link_callback_handles_absolute_urls(self):
        """Link callback deve retornar URLs absolutas sem modificação."""
        absolute_url = "https://example.com/style.css"

        result = self.mixin._pdf_link_callback(absolute_url, "")

        self.assertEqual(result, absolute_url)

        self.assertEqual(result, absolute_url)
