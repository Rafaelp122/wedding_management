"""
Testes para os formulários do app users.

Nota: Os testes da classe SignInForm foram removidos pois agora usamos
CustomLoginForm do django-allauth, que já é amplamente testado pela
biblioteca.
"""

from unittest.mock import patch

from django.test import RequestFactory, TestCase

from apps.users.models import User
from apps.users.web.forms import CustomUserChangeForm, CustomUserCreationForm


class CustomUserCreationFormTest(TestCase):
    def test_form_valid_registration(self):
        """
        Deve criar usuário se todos os dados estiverem corretos e senhas baterem.
        """
        data = {
            "username": "newuser",
            "email": "new@test.com",
            "first_name": "New",
            "last_name": "User",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        }
        form = CustomUserCreationForm(data=data)
        self.assertTrue(form.is_valid())

        # Salva e verifica se foi para o banco
        # O allauth precisa de um request com session
        from django.contrib.sessions.middleware import SessionMiddleware
        from django.http import HttpResponse

        request = RequestFactory().post("/fake-url")
        middleware = SessionMiddleware(lambda x: HttpResponse())  # type: ignore[arg-type]
        middleware.process_request(request)
        request.session.save()

        user = form.save(request)
        self.assertEqual(user.email, "new@test.com")
        self.assertTrue(user.check_password("StrongPass123!"))

    def test_form_invalid_password_mismatch(self):
        """
        Deve falhar se as senhas não forem iguais.
        """
        data = {
            "username": "mismatch",
            "email": "mis@test.com",
            "password1": "Pass123!",
            "password2": "DifferentPass123!",
        }
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_form_invalid_duplicate_email(self):
        """
        Deve falhar se tentar registrar email já existente (regra do Model).
        """
        # Cria usuário 1
        User.objects.create_user("u1", "exist@test.com", "123")

        # Tenta criar usuário 2 com mesmo email
        data = {
            "username": "u2",
            "email": "exist@test.com",  # Duplicado
            "password1": "Pass123!",
            "password2": "Pass123!",
        }
        form = CustomUserCreationForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    @patch("apps.users.forms.logger")
    def test_form_logs_warning_on_failure(self, mock_logger):
        """
        Verifica se o logger.warning é chamado quando o registro falha.
        """
        # Dados inválidos (senhas diferentes)
        data = {
            "username": "fail_log",
            "email": "fail@test.com",
            "password1": "123",
            "password2": "321",
        }
        form = CustomUserCreationForm(data=data)
        form.is_valid()  # Dispara a validação e o clean()

        # O logger deve ter sido chamado
        self.assertTrue(mock_logger.warning.called)
        # Verifica se a mensagem contém indício de erro
        args, _ = mock_logger.warning.call_args
        self.assertIn("Falha no registro", args[0])

    def test_form_has_large_css_classes(self):
        """
        Garante que o FormStylingMixinLarge foi aplicado no cadastro,
        deixando os inputs grandes.
        """
        form = CustomUserCreationForm()

        # Verifica um campo qualquer (ex: username)
        widget_class = form.fields["username"].widget.attrs.get("class", "")

        self.assertIn("form-control-lg", widget_class)
        self.assertIn("custom-font-size", widget_class)


class CustomUserChangeFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("edituser", "edit@test.com", "123")

    def test_form_updates_fields(self):
        """
        Deve atualizar os campos permitidos.
        """
        data = {
            "username": "edited_user",
            "first_name": "Edited",
            "last_name": "Name",
            "email": "edited@test.com",
        }
        form = CustomUserChangeForm(instance=self.user, data=data)
        self.assertTrue(form.is_valid())

        user = form.save()
        self.assertEqual(user.username, "edited_user")
        self.assertEqual(user.email, "edited@test.com")

    def test_password_field_is_removed(self):
        """
        O campo de senha não deve existir neste formulário.
        """
        form = CustomUserChangeForm(instance=self.user)
        self.assertNotIn("password", form.fields)
