"""
Testes dos serializers da API de Events (Scheduler).
"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from apps.scheduler.models import Event
from apps.scheduler.api.serializers import (
    EventSerializer,
    EventListSerializer,
    EventDetailSerializer,
)
from apps.weddings.models import Wedding

User = get_user_model()


class EventSerializerTest(TestCase):
    """Testes do EventSerializer (CRUD)."""

    def setUp(self):
        """Configuração inicial dos testes."""
        self.user = User.objects.create_user(
            username="planner",
            email="planner@example.com",
            password="test123"
        )
        self.wedding = Wedding.objects.create(
            planner=self.user,
            groom_name="João",
            bride_name="Maria",
            date="2025-12-31",
            location="São Paulo",
            budget=Decimal("50000.00")
        )

    def test_serialization(self):
        """Testa a serialização de um evento."""
        start = timezone.now()
        end = start + timedelta(hours=2)
        
        event = Event.objects.create(
            wedding=self.wedding,
            planner=self.user,
            title="Reunião com Buffet",
            description="Discutir cardápio",
            start_time=start,
            end_time=end,
            event_type="reuniao",
            location="Buffet Central"
        )

        serializer = EventSerializer(event)
        data = serializer.data

        self.assertEqual(data["id"], event.id)
        self.assertEqual(data["wedding"], self.wedding.id)
        self.assertEqual(data["title"], "Reunião com Buffet")
        self.assertEqual(data["event_type"], "reuniao")
        self.assertEqual(data["location"], "Buffet Central")

    def test_deserialization_valid(self):
        """Testa a desserialização com dados válidos."""
        start = timezone.now()
        end = start + timedelta(hours=1)
        
        data = {
            "wedding": self.wedding.id,
            "planner": self.user.id,
            "title": "Teste de Som",
            "description": "Verificar equipamentos",
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "event_type": "visita",
            "location": "Igreja Matriz",
        }

        serializer = EventSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        event = serializer.save()
        self.assertEqual(event.title, "Teste de Som")
        self.assertEqual(event.event_type, "visita")
        self.assertEqual(event.location, "Igreja Matriz")

    def test_validation_end_before_start(self):
        """Testa validação de horário de término anterior ao início."""
        start = timezone.now()
        end = start - timedelta(hours=1)  # Erro: end antes de start
        
        data = {
            "wedding": self.wedding.id,
            "planner": self.user.id,
            "title": "Evento Inválido",
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "event_type": "reuniao",
        }

        serializer = EventSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("end_time", serializer.errors)


class EventListSerializerTest(TestCase):
    """Testes do EventListSerializer (otimizado para listagem)."""

    def setUp(self):
        """Configuração inicial dos testes."""
        self.user = User.objects.create_user(
            username="planner",
            email="planner2@example.com",
            password="test123"
        )
        self.wedding = Wedding.objects.create(
            planner=self.user,
            groom_name="Pedro",
            bride_name="Ana",
            date="2025-06-15",
            location="Rio de Janeiro",
            budget=Decimal("40000.00")
        )

    def test_serialization_with_calculated_fields(self):
        """Testa serialização com campos calculados."""
        start = timezone.now()
        end = start + timedelta(hours=3)
        
        event = Event.objects.create(
            wedding=self.wedding,
            planner=self.user,
            title="Ensaio Fotográfico",
            start_time=start,
            end_time=end,
            event_type="visita",
        )

        serializer = EventListSerializer(event)
        data = serializer.data

        self.assertEqual(data["id"], event.id)
        self.assertEqual(data["title"], "Ensaio Fotográfico")
        self.assertEqual(data["wedding_couple"], "Pedro & Ana")
        self.assertEqual(data["duration_minutes"], 180)  # 3 horas

    def test_duration_calculation(self):
        """Testa o cálculo correto da duração."""
        start = timezone.now()
        end = start + timedelta(minutes=45)
        
        event = Event.objects.create(
            wedding=self.wedding,
            planner=self.user,
            title="Reunião Rápida",
            start_time=start,
            end_time=end,
            event_type="reuniao",
        )

        serializer = EventListSerializer(event)
        self.assertEqual(serializer.data["duration_minutes"], 45)


class EventDetailSerializerTest(TestCase):
    """Testes do EventDetailSerializer (detalhes completos)."""

    def setUp(self):
        """Configuração inicial dos testes."""
        self.user = User.objects.create_user(
            username="planner",
            email="planner3@example.com",
            password="test123"
        )
        self.wedding = Wedding.objects.create(
            planner=self.user,
            groom_name="Carlos",
            bride_name="Julia",
            date="2025-09-20",
            location="Belo Horizonte",
            budget=Decimal("45000.00")
        )

    def test_serialization_with_full_details(self):
        """Testa serialização com detalhes completos."""
        start = timezone.now() + timedelta(days=10)
        end = start + timedelta(hours=2)
        
        event = Event.objects.create(
            wedding=self.wedding,
            planner=self.user,
            title="Degustação do Buffet",
            description="Experimentar pratos do cardápio",
            start_time=start,
            end_time=end,
            event_type="degustacao",
            location="Restaurante Nobre",
        )

        serializer = EventDetailSerializer(event)
        data = serializer.data

        self.assertEqual(data["id"], event.id)
        self.assertEqual(data["title"], "Degustação do Buffet")
        self.assertEqual(data["wedding_couple"], "Carlos & Julia")
        self.assertIn("wedding_date", data)
        self.assertEqual(data["duration_minutes"], 120)
        self.assertFalse(data["is_past"])  # Evento futuro

    def test_is_past_flag(self):
        """Testa o flag is_past para eventos passados e futuros."""
        # Evento passado
        past_start = timezone.now() - timedelta(days=5)
        past_end = past_start + timedelta(hours=1)
        past_event = Event.objects.create(
            wedding=self.wedding,
            planner=self.user,
            title="Evento Passado",
            start_time=past_start,
            end_time=past_end,
            event_type="reuniao",
        )

        serializer_past = EventDetailSerializer(past_event)
        self.assertTrue(serializer_past.data["is_past"])

        # Evento futuro
        future_start = timezone.now() + timedelta(days=5)
        future_end = future_start + timedelta(hours=1)
        future_event = Event.objects.create(
            wedding=self.wedding,
            planner=self.user,
            title="Evento Futuro",
            start_time=future_start,
            end_time=future_end,
            event_type="visita",
        )

        serializer_future = EventDetailSerializer(future_event)
        self.assertFalse(serializer_future.data["is_past"])
