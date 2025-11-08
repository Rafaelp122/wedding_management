from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class SignUpViewTests(TestCase):
    def test_signup_page_loads_correctly_on_get(self):
        """Verifica se a página de cadastro carrega com sucesso (GET)."""
        response = self.client.get(reverse("users:sign_up"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/sign_up.html")
        # Verifica se o contexto customizado está presente
        self.assertIn("form_layout_dict", response.context)
        self.assertEqual(response.context["button_text"], "Enviar")

    def test_user_creation_fails_with_invalid_data(self):
        """Verifica se o cadastro falha quando as senhas não coincidem."""
        invalid_data = {
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "password1": "validpass123",
            "password2": "DIFFERENTpass123",
        }

        initial_user_count = User.objects.count()
        response = self.client.post(reverse("users:sign_up"), data=invalid_data)
        response.render()
        final_user_count = User.objects.count()

        self.assertEqual(response.status_code, 200)

        form = response.context.get("form")
        self.assertTrue(form.errors, "Esperava erros de validação no formulário")

        password_errors = form.errors.get("password2", [])
        self.assertIn(
            "Os dois campos de senha não correspondem.",
            password_errors,
            f"Mensagens encontradas: {password_errors}",
        )

        self.assertEqual(initial_user_count, final_user_count)

    def test_user_creation_succeeds_with_valid_data(self):
        """Verifica se o cadastro funciona com dados válidos (POST)."""
        valid_data = {
            "username": "newuser",
            "first_name": "New",
            "last_name": "User",
            "email": "new@example.com",
            "password1": "strongpass123",
            "password2": "strongpass123",
        }

        # Verifica o estado do banco ANTES da ação
        initial_user_count = User.objects.count()

        # Faz a requisição POST e já segue o redirecionamento
        response = self.client.post(
            reverse("users:sign_up"),
            data=valid_data,
            follow=True,  # Ação principal: envia o form e carrega a página de login
        )

        # Verifica se o usuário foi criado no banco DEPOIS da ação
        self.assertEqual(User.objects.count(), initial_user_count + 1)
        created_user = User.objects.get(username="newuser")
        self.assertEqual(created_user.email, "new@example.com")

        # Verifica se a mensagem de sucesso está na PÁGINA FINAL (página de login)
        self.assertContains(
            response, "Cadastro realizado com sucesso! Faça login para continuar."
        )

        # (Opcional) Verifica se o redirecionamento ocorreu corretamente
        self.assertEqual(len(response.redirect_chain), 1)
        self.assertEqual(response.redirect_chain[0][0], reverse("users:sign_in"))
        self.assertEqual(response.redirect_chain[0][1], 302)
