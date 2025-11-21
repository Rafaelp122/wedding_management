from unittest.mock import patch

from django.test import TestCase

from apps.users.models import User
from apps.users.web.forms import (CustomUserChangeForm, CustomUserCreationForm,
                                  SignInForm)


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
        user = form.save()
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
            "email": "exist@test.com", # Duplicado
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

    def test_inactive_user_cannot_login(self):
        """
        Usuário com is_active=False não deve conseguir logar,
        mesmo com a senha correta.
        """
        inactive_user = User.objects.create_user(
            "inactive", "in@test.com", "123", is_active=False
        )

        data = {
            "username": "inactive",
            "password": "123"  # Senha correta
        }
        form = SignInForm(request=None, data=data)

        self.assertFalse(form.is_valid())
        # O erro específico geralmente diz "Esta conta está inativa"
        self.assertIn("__all__", form.errors)

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


class SignInFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="loginuser",
            email="login@test.com",
            password="CorrectPassword123"
        )

    def test_form_valid_login(self):
        """
        Login com credenciais corretas deve ser válido.
        """
        data = {
            "username": "loginuser",
            "password": "CorrectPassword123"
        }
        # AuthenticationForm precisa do request (pode ser None nos testes simples)
        form = SignInForm(request=None, data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.get_user(), self.user)

    def test_form_invalid_login_wrong_password(self):
        """
        Login com senha errada deve falhar.
        """
        data = {
            "username": "loginuser",
            "password": "WrongPassword"
        }
        form = SignInForm(request=None, data=data)
        self.assertFalse(form.is_valid())
        # O erro genérico de login fica em __all__
        self.assertIn("__all__", form.errors)

    @patch("apps.users.forms.logger")
    def test_form_logs_warning_on_login_failure(self, mock_logger):
        """
        Verifica se o logger.warning é chamado quando o login falha.
        """
        data = {"username": "wrong", "password": "wrong"}
        form = SignInForm(request=None, data=data)
        form.is_valid()

        self.assertTrue(mock_logger.warning.called)
        args, _ = mock_logger.warning.call_args
        self.assertIn("Tentativa de login falhou", args[0])

    def test_form_has_large_css_classes(self):
        """
        Garante que o FormStylingMixinLarge foi aplicado corretamente.
        """
        form = SignInForm()
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
            "email": "edited@test.com"
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
