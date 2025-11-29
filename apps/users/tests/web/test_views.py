"""
Testes para as views do app users.

Nota: As views de signup, signin e logout agora são gerenciadas pelo
django-allauth. Esses testes foram removidos pois o allauth já é
amplamente testado pela própria biblioteca. Mantemos apenas os testes
das views customizadas que implementamos.
"""

from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from apps.users.models import User


class EditProfileViewTest(TestCase):
    """Testes para a view customizada de edição de perfil."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("edituser", "e@test.com", "123")

    def setUp(self):
        self.url = reverse("users:edit_profile")

    def test_anonymous_redirected_to_login(self):
        """Se não logado, redireciona."""
        response = self.client.get(self.url)
        expected_url = f"{reverse('account_login')}?next={self.url}"
        self.assertRedirects(response, expected_url)

    def test_get_renders_form_with_instance(self):
        """GET carrega dados do usuário logado."""
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["form"].instance, self.user)
        self.assertEqual(response.context["user"], self.user)

    def test_post_updates_profile(self):
        """POST atualiza dados."""
        self.client.force_login(self.user)
        data = {
            "username": "updated_user",
            "first_name": "Updated",
            "last_name": "Name",
            "email": "updated@test.com",
        }
        response = self.client.post(self.url, data)

        # Verifica banco
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "updated_user")
        self.assertEqual(self.user.email, "updated@test.com")

        # Redireciona para my_weddings (definido na View)
        self.assertRedirects(response, reverse("weddings:my_weddings"))

        messages = list(get_messages(response.wsgi_request))
        self.assertIn("Seu perfil foi atualizado", str(messages[0]))

    def test_post_update_invalid_data_shows_errors(self):
        """
        Se enviar dados vazios para campos obrigatórios (username/email),
        não deve salvar e deve mostrar erros.
        """
        self.client.force_login(self.user)

        # Username e Email vazios
        data = {
            "username": "",
            "email": "",
            "first_name": "Updated",
            "last_name": "Name",
        }
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)

        # Verifica se tem erros no form
        self.assertTrue(response.context["form"].errors)
        self.assertIn("username", response.context["form"].errors)
        self.assertIn("email", response.context["form"].errors)

        # Garante que o banco NÃO mudou
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.first_name, "Updated")

    def test_post_update_duplicate_email_fails(self):
        """
        Não deve permitir alterar o e-mail para um que já pertence
        a outro usuário.
        """
        # Cria um segundo usuário para "roubar" o email
        User.objects.create_user("other", "occupied@test.com", "123")

        self.client.force_login(self.user)

        data = {
            "username": "my_user",
            "email": "occupied@test.com",  # E-mail já em uso!
            "first_name": "Me",
            "last_name": "Myself",
        }
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)

        # O form deve acusar erro no email
        self.assertIn("email", response.context["form"].errors)

        # O email do usuário logado deve continuar o antigo
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.email, "occupied@test.com")
