from django.test import SimpleTestCase, TestCase
from unittest.mock import patch
from apps.pages.forms import ContactForm
from apps.pages.models import ContactInquiry


class ContactFormTest(SimpleTestCase):
    def test_form_valid_data(self):
        """
        Formulário deve ser válido com dados corretos.
        """
        data = {
            "name": "Cliente Feliz",
            "email": "cliente@teste.com",
            "message": "Adorei o serviço!"
        }
        form = ContactForm(data=data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_missing_required_fields(self):
        """
        Todos os campos (nome, email, mensagem) são obrigatórios.
        """
        data = {}  # Vazio
        form = ContactForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertIn("email", form.errors)
        self.assertIn("message", form.errors)

    def test_form_invalid_email_format(self):
        """
        O campo email deve validar formato.
        """
        data = {
            "name": "Teste",
            "email": "not-an-email",  # Inválido
            "message": "Hello"
        }
        form = ContactForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_widgets_and_placeholders(self):
        """
        Verifica se o __init__ aplicou placeholders e widgets corretamente.
        """
        form = ContactForm()

        # Placeholder
        self.assertEqual(
            form.fields["message"].widget.attrs["placeholder"],
            "Digite sua mensagem aqui..."
        )

        # Widget (rows=5 no Textarea)
        self.assertEqual(
            form.fields["message"].widget.attrs["rows"],
            5
        )

        # Mixin de estilo (FormStylingMixin adiciona form-control)
        self.assertIn(
            "form-control",
            form.fields["name"].widget.attrs["class"]
        )

    @patch("apps.pages.forms.logger")
    def test_logging_on_error(self, mock_logger):
        """
        Deve logar um warning se o formulário for inválido.
        """
        data = {"name": ""}  # Inválido
        form = ContactForm(data=data)

        # Força validação
        form.is_valid()

        self.assertTrue(mock_logger.warning.called)
        args, _ = mock_logger.warning.call_args
        self.assertIn("Erro no formulário de contato", args[0])


class ContactFormIntegrationTest(TestCase):
    def test_form_save_creates_model_instance(self):
        """
        Teste de Integração: O form.save() deve criar um registro no banco.
        """
        data = {
            "name": "Integração",
            "email": "integra@test.com",
            "message": "Salvando no banco."
        }
        form = ContactForm(data=data)

        self.assertTrue(form.is_valid())

        # Ação principal
        inquiry = form.save()

        # Verificações
        self.assertIsInstance(inquiry, ContactInquiry)
        self.assertEqual(inquiry.pk, 1)  # Primeiro registro
        self.assertTrue(ContactInquiry.objects.filter(email="integra@test.com").exists())
