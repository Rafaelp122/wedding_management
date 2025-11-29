"""
Testes para os serializers da API de Wedding.
"""

from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from apps.users.models import User
from apps.weddings.api.serializers import (
    WeddingDetailSerializer,
    WeddingListSerializer,
    WeddingSerializer,
)
from apps.weddings.models import Wedding


class WeddingSerializerTestCase(TestCase):
    """Testes para WeddingSerializer (CRUD)."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    def test_serializer_valid_data(self):
        """Testa se o serializer aceita dados válidos."""
        data = {
            "groom_name": "John",
            "bride_name": "Jane",
            "date": timezone.localdate() + timezone.timedelta(days=30),
            "location": "Church",
            "budget": "5000.00",
            "status": Wedding.StatusChoices.IN_PROGRESS,
        }

        serializer = WeddingSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_serializer_invalid_budget(self):
        """Testa se o serializer rejeita orçamento negativo."""
        data = {
            "groom_name": "John",
            "bride_name": "Jane",
            "date": timezone.localdate() + timezone.timedelta(days=30),
            "location": "Church",
            "budget": "-100.00",
            "status": Wedding.StatusChoices.IN_PROGRESS,
        }

        serializer = WeddingSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("budget", serializer.errors)

    def test_serializer_invalid_past_date(self):
        """Testa se o serializer rejeita data passada."""
        data = {
            "groom_name": "John",
            "bride_name": "Jane",
            "date": timezone.localdate() - timezone.timedelta(days=1),
            "location": "Church",
            "budget": "5000.00",
            "status": Wedding.StatusChoices.IN_PROGRESS,
        }

        serializer = WeddingSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("date", serializer.errors)


class WeddingListSerializerTestCase(TestCase):
    """Testes para WeddingListSerializer."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )
        self.wedding = Wedding.objects.create(
            planner=self.user,
            groom_name="John",
            bride_name="Jane",
            date=timezone.localdate() + timezone.timedelta(days=30),
            location="Church",
            budget=Decimal("5000.00"),
            status=Wedding.StatusChoices.IN_PROGRESS,
        )

    def test_serializer_contains_expected_fields(self):
        """Testa se o serializer retorna os campos esperados."""
        serializer = WeddingListSerializer(instance=self.wedding)
        data = serializer.data

        expected_fields = [
            "id",
            "couple_name",
            "groom_name",
            "bride_name",
            "date",
            "location",
            "status",
            "status_display",
            "planner_name",
            "created_at",
        ]

        for field in expected_fields:
            self.assertIn(field, data)

    def test_couple_name_format(self):
        """Testa se couple_name está formatado corretamente."""
        serializer = WeddingListSerializer(instance=self.wedding)
        self.assertEqual(serializer.data["couple_name"], "John & Jane")


class WeddingDetailSerializerTestCase(TestCase):
    """Testes para WeddingDetailSerializer."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )
        self.wedding = Wedding.objects.create(
            planner=self.user,
            groom_name="John",
            bride_name="Jane",
            date=timezone.localdate() + timezone.timedelta(days=30),
            location="Church",
            budget=Decimal("5000.00"),
            status=Wedding.StatusChoices.IN_PROGRESS,
        )

    def test_serializer_contains_detailed_fields(self):
        """Testa se o serializer retorna campos detalhados."""
        serializer = WeddingDetailSerializer(instance=self.wedding)
        data = serializer.data

        expected_fields = [
            "id",
            "couple_name",
            "groom_name",
            "bride_name",
            "date",
            "location",
            "budget",
            "status",
            "status_display",
            "planner_name",
            "planner_email",
            "items_count",
            "contracts_count",
            "created_at",
            "updated_at",
        ]

        for field in expected_fields:
            self.assertIn(field, data)

    def test_planner_email_included(self):
        """Testa se o email do planner está incluído."""
        serializer = WeddingDetailSerializer(instance=self.wedding)
        self.assertEqual(serializer.data["planner_email"], "test@example.com")
