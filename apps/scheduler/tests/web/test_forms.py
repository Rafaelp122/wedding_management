"""
Testes para o EventForm do app scheduler.
"""

from datetime import date, time, timedelta

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
            "event_date": date.today() + timedelta(days=7),
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
        self.assertIn("event_date", form.errors)
        self.assertIn("start_time_input", form.errors)

    def test_form_end_time_before_start_time(self):
        """Testa validação: horário de fim antes do início."""
        form_data = {
            "title": "Evento Teste",
            "event_date": date.today() + timedelta(days=7),
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
            "event_date": date.today() + timedelta(days=7),
            "start_time_input": time(14, 0),
            "end_time_input": time(14, 0),  # Igual ao início
            "event_type": Event.TypeChoices.OTHER,
        }

        form = EventForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("end_time_input", form.errors)

    def test_form_save_combines_date_and_time(self):
        """Testa que o save() combina data e hora corretamente."""
        form_data = {
            "title": "Reunião Teste",
            "event_date": date(2025, 12, 15),
            "start_time_input": time(14, 30),
            "end_time_input": time(16, 0),
            "event_type": Event.TypeChoices.MEETING,
        }

        form = EventForm(data=form_data)

        self.assertTrue(form.is_valid())

        event = form.save(commit=False)
        event.planner = self.user
        event.wedding = self.wedding
        event.save()

        # Verifica que start_time foi criado corretamente
        self.assertEqual(event.start_time.date(), date(2025, 12, 15))
        self.assertEqual(event.start_time.time(), time(14, 30))

        # Verifica que end_time foi criado corretamente
        self.assertEqual(event.end_time.date(), date(2025, 12, 15))
        self.assertEqual(event.end_time.time(), time(16, 0))

    def test_form_without_end_time(self):
        """Testa formulário sem horário de término (opcional)."""
        form_data = {
            "title": "Evento sem fim",
            "event_date": date.today() + timedelta(days=7),
            "start_time_input": time(14, 0),
            "event_type": Event.TypeChoices.OTHER,
        }

        form = EventForm(data=form_data)

        self.assertTrue(form.is_valid())

        event = form.save(commit=False)
        event.planner = self.user
        event.save()

        self.assertIsNotNone(event.start_time)
        self.assertIsNone(event.end_time)

    def test_form_with_clicked_date(self):
        """Testa que clicked_date preenche event_date."""
        clicked = "2025-12-20"
        form = EventForm(clicked_date=clicked)

        self.assertEqual(str(form.fields["event_date"].initial), clicked)

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

        # Verificar que campos foram preenchidos
        self.assertEqual(form.fields["event_date"].initial, date(2025, 12, 15))
        self.assertEqual(form.fields["start_time_input"].initial, time(14, 0))
        self.assertEqual(form.fields["end_time_input"].initial, time(16, 0))

    def test_form_optional_fields(self):
        """Testa que campos opcionais podem ser omitidos."""
        form_data = {
            "title": "Evento Mínimo",
            "event_date": date.today() + timedelta(days=7),
            "start_time_input": time(14, 0),
            "event_type": Event.TypeChoices.OTHER,
            # location, description e end_time_input omitidos
        }

        form = EventForm(data=form_data)

        self.assertTrue(form.is_valid())

        event = form.save(commit=False)
        event.planner = self.user

        self.assertEqual(event.title, "Evento Mínimo")
        self.assertEqual(event.location, "")
        # description retorna string vazia, não None
        self.assertEqual(event.description, "")

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

        # Verifica que os campos foram preenchidos corretamente
        local_start = timezone.localtime(event.start_time)
        local_end = timezone.localtime(event.end_time)

        self.assertEqual(form.fields["event_date"].initial, local_start.date())
        self.assertEqual(form.fields["start_time_input"].initial, local_start.time())
        self.assertEqual(form.fields["end_time_input"].initial, local_end.time())

    def test_form_save_combines_date_and_time_correctly(self):
        """Testa que o form.save() combina data + hora corretamente."""
        form_data = {
            "title": "Reunião Importante",
            "event_type": Event.TypeChoices.MEETING,
            "event_date": date.today() + timedelta(days=5),
            "start_time_input": time(10, 30),
            "end_time_input": time(12, 0),
        }

        form = EventForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Salva sem commit para inspecionar
        event = form.save(commit=False)
        event.wedding = self.wedding
        event.planner = self.user  # Campo obrigatório
        event.save()

        # Verifica que start_time foi combinado corretamente
        expected_start = timezone.make_aware(
            timezone.datetime.combine(
                form_data["event_date"], form_data["start_time_input"]
            )
        )
        expected_end = timezone.make_aware(
            timezone.datetime.combine(
                form_data["event_date"], form_data["end_time_input"]
            )
        )

        self.assertEqual(event.start_time, expected_start)
        self.assertEqual(event.end_time, expected_end)
