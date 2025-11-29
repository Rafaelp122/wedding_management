"""
Testes para o modelo Event do app scheduler.
"""

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.scheduler.models import Event
from apps.users.models import User
from apps.weddings.models import Wedding


class EventModelTest(TestCase):
    """Testes para o modelo Event."""

    @classmethod
    def setUpTestData(cls):
        """Configuração inicial para os testes."""
        cls.user = User.objects.create_user(
            username="testplanner",
            email="planner@test.com",
            password="testpass123",
        )

        cls.wedding = Wedding.objects.create(
            planner=cls.user,
            groom_name="João",
            bride_name="Maria",
            date=timezone.now().date() + timedelta(days=180),
            location="Salão de Festas",
            budget=50000.00,
        )

    def test_event_creation(self):
        """Testa a criação de um evento."""
        event = Event.objects.create(
            wedding=self.wedding,
            planner=self.user,
            title="Reunião com Buffet",
            location="Restaurante Central",
            description="Escolher menu do casamento",
            event_type=Event.TypeChoices.MEETING,
            start_time=timezone.now() + timedelta(days=7),
        )

        self.assertEqual(event.title, "Reunião com Buffet")
        self.assertEqual(event.planner, self.user)
        self.assertEqual(event.wedding, self.wedding)
        self.assertEqual(event.event_type, Event.TypeChoices.MEETING)

    def test_event_str_method(self):
        """Testa o método __str__ do evento."""
        event = Event.objects.create(
            wedding=self.wedding,
            planner=self.user,
            title="Degustação de Bolos",
            start_time=timezone.now(),
        )

        self.assertEqual(str(event), "Degustação de Bolos")

    def test_event_without_wedding(self):
        """Testa criar evento sem casamento vinculado."""
        event = Event.objects.create(
            planner=self.user,
            title="Reunião Geral",
            start_time=timezone.now(),
        )

        self.assertIsNone(event.wedding)
        self.assertEqual(event.planner, self.user)

    def test_event_with_end_time(self):
        """Testa evento com horário de término."""
        start = timezone.now() + timedelta(days=5)
        end = start + timedelta(hours=2)

        event = Event.objects.create(
            wedding=self.wedding,
            planner=self.user,
            title="Visita ao Local",
            start_time=start,
            end_time=end,
        )

        self.assertEqual(event.start_time, start)
        self.assertEqual(event.end_time, end)

    def test_event_type_choices(self):
        """Testa os tipos de eventos disponíveis."""
        choices = Event.TypeChoices.choices

        self.assertEqual(len(choices), 5)
        self.assertIn(("reuniao", "Reunião"), choices)
        self.assertIn(("pagamento", "Pagamento"), choices)
        self.assertIn(("visita", "Visita Técnica"), choices)
        self.assertIn(("degustacao", "Degustação"), choices)
        self.assertIn(("outro", "Outro"), choices)

    def test_event_default_type(self):
        """Testa o tipo padrão do evento."""
        event = Event.objects.create(
            wedding=self.wedding,
            planner=self.user,
            title="Evento sem tipo",
            start_time=timezone.now(),
        )

        self.assertEqual(event.event_type, Event.TypeChoices.OTHER)

    def test_event_cascade_delete_wedding(self):
        """Testa que eventos são deletados quando casamento é deletado."""
        Event.objects.create(
            wedding=self.wedding,
            planner=self.user,
            title="Evento 1",
            start_time=timezone.now(),
        )

        Event.objects.create(
            wedding=self.wedding,
            planner=self.user,
            title="Evento 2",
            start_time=timezone.now(),
        )

        self.assertEqual(Event.objects.count(), 2)

        self.wedding.delete()

        self.assertEqual(Event.objects.count(), 0)

    def test_event_cascade_delete_user(self):
        """Testa que eventos são deletados quando usuário é deletado."""
        Event.objects.create(
            wedding=self.wedding,
            planner=self.user,
            title="Evento Teste",
            start_time=timezone.now(),
        )

        self.assertEqual(Event.objects.count(), 1)

        self.user.delete()

        self.assertEqual(Event.objects.count(), 0)

    def test_event_optional_fields(self):
        """Testa que campos opcionais podem ser nulos."""
        event = Event.objects.create(
            planner=self.user,
            title="Evento Mínimo",
            start_time=timezone.now(),
        )

        self.assertIsNone(event.wedding)
        self.assertIsNone(event.location)
        self.assertIsNone(event.description)
        self.assertIsNone(event.end_time)
