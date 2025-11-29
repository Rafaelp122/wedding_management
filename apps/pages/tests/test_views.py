from unittest.mock import patch

from django.conf import settings
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from apps.pages.models import ContactInquiry
from apps.users.models import User


class HomeViewTest(TestCase):
    def setUp(self):
        self.url = reverse("pages:home")

    def test_get_renders_home_template(self):
        """Usuário anônimo deve ver a home."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/home.html")
        self.assertIn("contact_form", response.context)
        self.assertIn("form_icons", response.context)

    def test_authenticated_user_redirects_to_dashboard(self):
        """
        Usuário logado deve ser redirecionado para 'weddings:my_weddings'.
        (Testando o RedirectAuthenticatedUserMixin)
        """
        user = User.objects.create_user("user", "u@test.com", "123")
        self.client.force_login(user)

        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("weddings:my_weddings"))


class ContactFormSubmitViewTest(TestCase):
    def setUp(self):
        self.url = reverse("pages:contact_submit")

    def test_post_valid_saves_db_and_sends_email(self):
        """
        Submissão válida deve criar registro no banco, enviar email e retornar sucesso.
        """
        data = {"name": "Tester", "email": "test@valid.com", "message": "Hello World"}

        # Limpa a caixa de saída de email (mock do Django)
        mail.outbox = []

        response = self.client.post(self.url, data)

        # Verifica resposta HTTP (200 OK) e Template HTMX de Sucesso
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/partials/home/_contact_success.html")

        # Verifica Banco de Dados
        self.assertTrue(ContactInquiry.objects.filter(email="test@valid.com").exists())

        # Verifica Envio de E-mail
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Nova Mensagem de Contato de Tester")
        self.assertIn(settings.ADMIN_EMAIL, mail.outbox[0].to)

    def test_post_invalid_returns_400_and_form_errors(self):
        """
        Dados inválidos devem retornar status 400 e o form com erros.
        """
        data = {
            "name": "",  # Obrigatório
            "email": "invalid-email",  # Formato errado
            "message": "",
        }

        response = self.client.post(self.url, data)

        # Verifica Status 400 (Bad Request) - Importante para HTMX
        self.assertEqual(response.status_code, 400)

        # Verifica Template do Formulário (para re-renderizar com erros)
        self.assertTemplateUsed(
            response, "pages/partials/home/_contact_form_partial.html"
        )

        # Verifica se o Contexto tem os Erros
        self.assertTrue(response.context["contact_form"].errors)

        # Verifica se os Ícones foram reinjetados
        self.assertIn("form_icons", response.context)

        # Garante que NÃO salvou no banco
        self.assertEqual(ContactInquiry.objects.count(), 0)
        # Garante que NÃO enviou email
        self.assertEqual(len(mail.outbox), 0)

    @patch("apps.pages.views.send_mail")
    @patch("apps.pages.views.logger")
    def test_email_failure_is_handled_gracefully(self, mock_logger, mock_send_mail):
        """
        Se o envio de e-mail falhar, deve salvar no banco e retornar sucesso pro usuário
        (não deve dar erro 500), mas deve logar o erro.
        """
        # Simula exceção no envio de email
        mock_send_mail.side_effect = Exception("SMTP Server Down")

        data = {"name": "Tester", "email": "t@t.com", "message": "Msg"}

        response = self.client.post(self.url, data)

        # Deve retornar sucesso para o usuário (200)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/partials/home/_contact_success.html")

        # Deve ter salvo no banco
        self.assertTrue(ContactInquiry.objects.exists())

        # O logger deve ter sido chamado com o erro
        self.assertTrue(mock_logger.error.called)

    def test_get_request_returns_405(self):
        """
        A view ContactFormSubmitView aceita apenas POST.
        GET deve retornar 405 Method Not Allowed.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
