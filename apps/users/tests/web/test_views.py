from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from apps.users.models import User


class SignUpViewTest(TestCase):
    def setUp(self):
        self.url = reverse("users:sign_up")

    def test_get_renders_form(self):
        """Acesso GET deve renderizar o template com o form."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/sign_up.html")
        self.assertIn("form", response.context)
        # Verifica se o contexto extra (layout) foi passado
        self.assertIn("form_icons", response.context)

    def test_post_valid_creates_user(self):
        """POST válido deve criar usuário e redirecionar para login."""
        data = {
            "username": "newuser",
            "email": "new@test.com",
            "first_name": "New",
            "last_name": "User",
            "password1": "Pass123!",
            "password2": "Pass123!",
        }
        response = self.client.post(self.url, data)

        # Verifica criação no banco
        self.assertTrue(User.objects.filter(email="new@test.com").exists())

        # Verifica Redirecionamento
        self.assertRedirects(response, reverse("users:sign_in"))

        # Verifica Mensagem de Sucesso
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("Cadastro realizado", str(messages[0]))

    def test_post_invalid_shows_errors(self):
        """POST inválido (senhas diferentes) deve re-renderizar form."""
        data = {
            "username": "newuser",
            "email": "new@test.com",
            "password1": "123",
            "password2": "321",  # Errado
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email="new@test.com").exists())
        self.assertTrue(response.context["form"].errors)


class SignInViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("loginuser", "l@test.com", "123")
        self.url = reverse("users:sign_in")

    def test_get_renders_template(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/sign_in.html")

    def test_login_success(self):
        """Login válido deve redirecionar e autenticar."""
        data = {"username": "loginuser", "password": "123"}
        response = self.client.post(self.url, data)

        # Redireciona para LOGIN_REDIRECT_URL ou next (padrão Django)
        # Como não definimos next no teste, verificamos se logou
        self.assertTrue(response.wsgi_request.user.is_authenticated)

        # Verifica mensagem
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("Login bem sucedido", str(messages[0]))

    def test_login_failure(self):
        """Senha errada deve mostrar erro."""
        data = {"username": "loginuser", "password": "WRONG"}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

        # Verifica mensagem de erro (implementada no form_invalid)
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("Usuário ou senha inválidos", str(messages[0]))

    def test_authenticated_user_redirected(self):
        """Usuário já logado deve ser chutado pelo RedirectAuthenticatedUserMixin."""
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        # 302 para 'weddings:my_weddings' (definido no Mixin)
        self.assertEqual(response.status_code, 302)
        self.assertIn("my-weddings", response.url)


class EditProfileViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("edituser", "e@test.com", "123")
        self.url = reverse("users:edit_profile")

    def test_anonymous_redirected_to_login(self):
        """Se não logado, redireciona."""
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('users:sign_in')}?next={self.url}")

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
            "email": "updated@test.com"
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
            "last_name": "Name"
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
        Não deve permitir alterar o e-mail para um que já pertence a outro usuário.
        """
        # Cria um segundo usuário para "roubar" o email
        User.objects.create_user("other", "occupied@test.com", "123")

        self.client.force_login(self.user)

        data = {
            "username": "my_user",
            "email": "occupied@test.com",  # E-mail já em uso!
            "first_name": "Me",
            "last_name": "Myself"
        }
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)

        # O form deve acusar erro no email
        self.assertIn("email", response.context["form"].errors)

        # O email do usuário logado deve continuar o antigo
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.email, "occupied@test.com")


class LogoutViewTest(TestCase):
    def test_logout(self):
        """Testa se o logout realmente ocorre via POST."""
        user = User.objects.create_user("out", "out@test.com", "123")
        self.client.force_login(user)

        url = reverse("users:logout")

        response = self.client.post(url)

        # Verifica se redirecionou para login (configurado no urls.py)
        self.assertRedirects(response, reverse("users:sign_in"))

        # Verifica se o usuário não está mais autenticado na sessão
        session = self.client.session
        self.assertFalse("_auth_user_id" in session)
