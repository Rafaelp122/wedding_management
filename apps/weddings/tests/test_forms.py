from datetime import timedelta

from django.test import SimpleTestCase
from django.utils import timezone

from apps.weddings.forms import WeddingForm


class WeddingFormTest(SimpleTestCase):
    def setUp(self):
        # Define uma data válida (amanhã) para reuso
        self.future_date = timezone.localdate() + timedelta(days=1)

    def test_form_valid_data(self):
        """
        O formulário deve ser válido com dados corretos.
        """
        data = {
            "groom_name": "Romeu",
            "bride_name": "Julieta",
            "date": self.future_date,
            "budget": 50000.00,
            "location": "Verona",
        }
        form = WeddingForm(data=data)

        self.assertTrue(form.is_valid())

    def test_form_invalid_budget_zero(self):
        """
        O formulário deve falhar se o orçamento for zero.
        """
        data = {
            "groom_name": "Romeu",
            "bride_name": "Julieta",
            "date": self.future_date,
            "budget": 0,  # Inválido
            "location": "Verona",
        }
        form = WeddingForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("budget", form.errors)
        self.assertEqual(form.errors["budget"][0], "O orçamento deve ser maior que zero.")

    def test_form_invalid_budget_negative(self):
        """
        O formulário deve falhar se o orçamento for negativo.
        """
        data = {
            "groom_name": "Romeu",
            "bride_name": "Julieta",
            "date": self.future_date,
            "budget": -100,  # Inválido
            "location": "Verona",
        }
        form = WeddingForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("budget", form.errors)

    def test_form_invalid_past_date(self):
        """
        O formulário deve falhar se a data for no passado.
        """
        past_date = timezone.localdate() - timedelta(days=1)

        data = {
            "groom_name": "Romeu",
            "bride_name": "Julieta",
            "date": past_date, # Inválido
            "budget": 50000.00,
            "location": "Verona",
        }
        form = WeddingForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("date", form.errors)
        self.assertEqual(
            form.errors["date"][0], 
            "A data do casamento não pode ser anterior ao dia atual."
        )

    def test_form_today_date_is_valid(self):
        """
        Um casamento HOJE deve ser válido (limite da borda).
        """
        today = timezone.localdate()

        data = {
            "groom_name": "Romeu",
            "bride_name": "Julieta",
            "date": today, # Válido
            "budget": 50000.00,
            "location": "Verona",
        }
        form = WeddingForm(data=data)

        self.assertTrue(form.is_valid())

    def test_form_placeholders_and_widgets(self):
        """
        Testa se o __init__ aplicou os placeholders e se o widget de data está correto.
        """
        form = WeddingForm()

        # Verifica placeholder
        self.assertEqual(
            form.fields["groom_name"].widget.attrs.get("placeholder"),
            "Ex: Flavio"
        )

        # Verifica widget type="date" (Usamos .get() para evitar KeyError se falhar)
        widget_type = form.fields["date"].widget.attrs.get("type")
        self.assertEqual(widget_type, "date", "O campo Data deve ter o atributo type='date' para ativar o calendário HTML5.")

    def test_form_missing_required_fields(self):
        """
        Testa campos obrigatórios padrão do Model.
        """
        data = {}  # Vazio
        form = WeddingForm(data=data)

        self.assertFalse(form.is_valid())
        # Todos esses campos são required=True no model
        self.assertIn("groom_name", form.errors)
        self.assertIn("bride_name", form.errors)
        self.assertIn("budget", form.errors)
        self.assertIn("location", form.errors)
        self.assertIn("date", form.errors)
