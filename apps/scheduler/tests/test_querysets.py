"""
Testes para o EventQuerySet do app scheduler.
"""
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.scheduler.models import Event
from apps.users.models import User
from apps.weddings.models import Wedding


class EventQuerySetTest(TestCase):
    """Testes para o EventQuerySet."""

    @classmethod
    def setUpTestData(cls):
        """Configuração inicial (executado uma vez por classe)."""
        # Criar usuários
        cls.user1 = User.objects.create_user(
            username="planner1",
            email="planner1@test.com",
            password="testpass123",
        )

        cls.user2 = User.objects.create_user(
            username="planner2",
            email="planner2@test.com",
            password="testpass123",
        )

        cls.user3 = User.objects.create_user(
            username="planner3",
            email="planner3@test.com",
            password="testpass123",
        )

        # Criar casamentos
        cls.wedding1 = Wedding.objects.create(
            planner=cls.user1,
            groom_name="João",
            bride_name="Maria",
            date=timezone.now().date() + timedelta(days=180),
            budget=50000.00,
        )

        cls.wedding2 = Wedding.objects.create(
            planner=cls.user1,
            groom_name="Pedro",
            bride_name="Ana",
            date=timezone.now().date() + timedelta(days=200),
            budget=40000.00,
        )

        # Criar eventos do user1
        cls.event1 = Event.objects.create(
            wedding=cls.wedding1,
            planner=cls.user1,
            title="Evento 1 do Wedding 1",
            start_time=timezone.now() + timedelta(days=7),
        )

        cls.event2 = Event.objects.create(
            wedding=cls.wedding1,
            planner=cls.user1,
            title="Evento 2 do Wedding 1",
            start_time=timezone.now() + timedelta(days=14),
        )

        cls.event3 = Event.objects.create(
            wedding=cls.wedding2,
            planner=cls.user1,
            title="Evento do Wedding 2",
            start_time=timezone.now() + timedelta(days=21),
        )

        # Criar evento do user2
        cls.event4 = Event.objects.create(
            planner=cls.user2,
            title="Evento do User 2",
            start_time=timezone.now() + timedelta(days=28),
        )

    def test_for_planner(self):
        """Testa filtro por planner."""
        events_user1 = Event.objects.for_planner(self.user1)
        events_user2 = Event.objects.for_planner(self.user2)

        self.assertEqual(events_user1.count(), 3)
        self.assertEqual(events_user2.count(), 1)

        self.assertIn(self.event1, events_user1)
        self.assertIn(self.event2, events_user1)
        self.assertIn(self.event3, events_user1)
        self.assertNotIn(self.event4, events_user1)

    def test_for_wedding_id(self):
        """Testa filtro por ID do casamento."""
        events_wedding1 = Event.objects.for_wedding_id(self.wedding1.id)
        events_wedding2 = Event.objects.for_wedding_id(self.wedding2.id)

        self.assertEqual(events_wedding1.count(), 2)
        self.assertEqual(events_wedding2.count(), 1)

        self.assertIn(self.event1, events_wedding1)
        self.assertIn(self.event2, events_wedding1)
        self.assertNotIn(self.event3, events_wedding1)

    def test_queryset_chaining(self):
        """Testa encadeamento de métodos do QuerySet."""
        # Filtrar por planner e depois por casamento
        events = Event.objects.for_planner(self.user1).for_wedding_id(
            self.wedding1.id
        )

        self.assertEqual(events.count(), 2)
        self.assertIn(self.event1, events)
        self.assertIn(self.event2, events)
        self.assertNotIn(self.event3, events)

    def test_queryset_with_standard_methods(self):
        """Testa que métodos padrão do QuerySet ainda funcionam."""
        # Usar métodos customizados + métodos padrão
        events = Event.objects.for_planner(self.user1).order_by("title")

        self.assertEqual(events.count(), 3)
        self.assertEqual(events.first().title, "Evento 1 do Wedding 1")

    def test_queryset_empty_result(self):
        """Testa que filtros retornam queryset vazio quando apropriado."""
        # Usar usuário já criado no setUpTestData ao invés de criar novo
        events = Event.objects.for_planner(self.user3)

        self.assertEqual(events.count(), 0)
        self.assertFalse(events.exists())
