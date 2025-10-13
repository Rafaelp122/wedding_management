# users/tests/test_views.py

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class SignInViewTests(TestCase):
    def setUp(self):
        """Cria um usuário de teste antes de cada teste de login."""
        self.credentials = {
            'username': 'testuser',
            'password': 'secretpassword123',
            'email': 'test@example.com',
        }
        self.user = User.objects.create_user(**self.credentials)

    def test_signin_page_loads_correctly_on_get(self):
        """Verifica se a página de login carrega com sucesso (GET)."""
        response = self.client.get(reverse('users:sign_in'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/sign_in.html')
        self.assertEqual(response.context['button_text'], 'Entrar')

    def test_login_fails_with_invalid_credentials(self):
        """Verifica se o login falha com credenciais erradas (POST)."""
        invalid_credentials = {
            'username': 'testuser',
            'password': 'wrongpassword',  # Senha errada
        }

        response = self.client.post(reverse('users:sign_in'), data=invalid_credentials)

        self.assertEqual(response.status_code, 200)  # Sem redirecionamento
        # Verifica se o usuário NÃO está logado na sessão
        self.assertNotIn('_auth_user_id', self.client.session)
        # Verifica a mensagem de erro da sua view
        self.assertContains(response, 'Usuário ou senha inválidos')

    def test_login_succeeds_with_valid_credentials(self):
        """Verifica se o login funciona com credenciais corretas (POST)."""

        # 1. Faz a requisição POST e já segue o redirecionamento
        response = self.client.post(
            reverse('users:sign_in'),
            data=self.credentials,
            follow=True  # Simula o clique e o carregamento da próxima página
        )

        # 2. Verifica se a mensagem de sucesso está no conteúdo da PÁGINA FINAL
        #    'assertContains' é um atalho do Django que já decodifica o 'response.content'
        self.assertContains(response, "Login bem sucedido!")

        # 3. Garante que a sessão do usuário foi criada corretamente
        self.assertIn('_auth_user_id', self.client.session)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.id)
