"""
Testes para o EventForm do app scheduler.
"""

from datetime import time, timedelta

from django.test import TestCase
from django.utils import timezone

from apps.scheduler.models import Event
from apps.scheduler.web.forms import EventForm
from apps.users.models import User
from apps.weddings.models import Wedding


class EventFormTest(TestCase):
    """Testes para o EventForm."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.user = User.objects.create_user(
            username="testplanner",
            email="planner@test.com",
            password="testpass123",
        )

        self.wedding = Wedding.objects.create(
            planner=self.user,
            groom_name="João",
            bride_name="Maria",
            date=timezone.now().date() + timedelta(days=180),
            budget=50000.00,
        )

    def test_form_valid_data(self):
        """Testa formulário com dados válidos."""
        form_data = {
            "title": "Reunião com Buffet",
            "location": "Restaurante Central",
            "description": "Escolher menu",
            "event_type": Event.TypeChoices.MEETING,
            "start_time_input": time(14, 0),
            "end_time_input": time(16, 0),
        }

        form = EventForm(data=form_data)

        self.assertTrue(form.is_valid())

    def test_form_missing_required_fields(self):
        """Testa formulário sem campos obrigatórios."""
        form_data = {
            "location": "Algum lugar",
        }

        form = EventForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)
        self.assertIn("start_time_input", form.errors)

    def test_form_end_time_before_start_time(self):
        """Testa validação: horário de fim antes do início."""
        form_data = {
            "title": "Evento Teste",
            "start_time_input": time(16, 0),
            "end_time_input": time(14, 0),  # Antes do início
            "event_type": Event.TypeChoices.OTHER,
        }

        form = EventForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("end_time_input", form.errors)
        self.assertIn(
            "deve ser posterior ao horário de início",
            form.errors["end_time_input"][0],
        )

    def test_form_end_time_equal_start_time(self):
        """Testa validação: horário de fim igual ao início."""
        form_data = {
            "title": "Evento Teste",
            "start_time_input": time(14, 0),
            "end_time_input": time(14, 0),  # Igual ao início
            "event_type": Event.TypeChoices.OTHER,
        }

        form = EventForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("end_time_input", form.errors)

    def test_form_get_time_methods(self):
        """Testa que os métodos get_start_time_input e get_end_time_input funcionam."""
        form_data = {
            "title": "Reunião Teste",
            "start_time_input": time(14, 30),
            "end_time_input": time(16, 0),
            "event_type": Event.TypeChoices.MEETING,
        }

        form = EventForm(data=form_data)

        self.assertTrue(form.is_valid())

        # Verifica que os métodos retornam os horários corretamente
        self.assertEqual(form.get_start_time_input(), time(14, 30))
        self.assertEqual(form.get_end_time_input(), time(16, 0))

    def test_form_without_end_time(self):
        """Testa formulário sem horário de término (opcional)."""
        form_data = {
            "title": "Evento sem fim",
            "start_time_input": time(14, 0),
            "event_type": Event.TypeChoices.OTHER,
        }

        form = EventForm(data=form_data)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.get_start_time_input(), time(14, 0))
        self.assertIsNone(form.get_end_time_input())

    def test_form_edit_existing_event(self):
        """Testa edição de evento existente."""
        # Criar evento
        event = Event.objects.create(
            wedding=self.wedding,
            planner=self.user,
            title="Evento Original",
            start_time=timezone.make_aware(timezone.datetime(2025, 12, 15, 14, 0)),
            end_time=timezone.make_aware(timezone.datetime(2025, 12, 15, 16, 0)),
        )

        # Carregar formulário com instância
        form = EventForm(instance=event)

        # Verificar que campos de hora foram preenchidos
        self.assertEqual(form.fields["start_time_input"].initial, time(14, 0))
        self.assertEqual(form.fields["end_time_input"].initial, time(16, 0))

    def test_form_optional_fields(self):
        """Testa que campos opcionais podem ser omitidos."""
        form_data = {
            "title": "Evento Mínimo",
            "start_time_input": time(14, 0),
            "event_type": Event.TypeChoices.OTHER,
            # location, description e end_time_input omitidos
        }

        form = EventForm(data=form_data)

        self.assertTrue(form.is_valid())

    def test_form_has_bootstrap_classes(self):
        """Testa que FormStylingMixin aplica classes CSS."""
        form = EventForm()

        # Verifica que campos têm classes Bootstrap
        title_widget_attrs = form.fields["title"].widget.attrs
        self.assertIn("class", title_widget_attrs)
        self.assertIn("form-control", title_widget_attrs["class"])

    def test_form_fills_fields_when_editing_event(self):
        """Testa que form preenche data/hora ao editar evento existente."""
        # Cria um evento com horários específicos
        event_datetime = timezone.now() + timedelta(days=10, hours=3)
        event = Event.objects.create(
            wedding=self.wedding,
            planner=self.user,  # Campo obrigatório
            title="Evento Teste",
            event_type=Event.TypeChoices.MEETING,
            start_time=event_datetime,
            end_time=event_datetime + timedelta(hours=2),
        )

        # Cria o form passando a instância
        form = EventForm(instance=event)

        # Verifica que os campos de hora foram preenchidos corretamente
        local_start = timezone.localtime(event.start_time)
        local_end = timezone.localtime(event.end_time)

        self.assertEqual(form.fields["start_time_input"].initial, local_start.time())
        self.assertEqual(form.fields["end_time_input"].initial, local_end.time())

    def test_form_get_methods_return_correct_values(self):
        """Testa que get_start_time_input e get_end_time_input retornam
        valores corretos."""
        form_data = {
            "title": "Reunião Importante",
            "event_type": Event.TypeChoices.MEETING,
            "start_time_input": time(10, 30),
            "end_time_input": time(12, 0),
        }

        form = EventForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Verifica que os métodos retornam os valores corretos
        self.assertEqual(form.get_start_time_input(), time(10, 30))
        self.assertEqual(form.get_end_time_input(), time(12, 0))
