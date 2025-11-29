"""
Testes dos serializers da API de Items.
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.items.api.serializers import (
    ItemDetailSerializer,
    ItemListSerializer,
    ItemSerializer,
)
from apps.items.models import Item
from apps.weddings.models import Wedding

User = get_user_model()


class ItemSerializerTest(TestCase):
    """Testes do ItemSerializer (CRUD)."""

    @classmethod
    def setUpTestData(cls):
        """Configuração inicial dos testes."""
        cls.user = User.objects.create_user(
            username="planner", email="planner@example.com", password="test123"
        )
        cls.wedding = Wedding.objects.create(
            planner=cls.user,
            groom_name="João",
            bride_name="Maria",
            date="2025-12-31",
            location="São Paulo",
            budget=Decimal("50000.00"),
        )

    def test_serialization(self):
        """Testa a serialização de um item."""
        item = Item.objects.create(
            wedding=self.wedding,
            name="Buffet",
            category="FOOD",
            quantity=1,
            unit_price=Decimal("5000.00"),
            status="PENDING",
        )

        serializer = ItemSerializer(item)
        data = serializer.data

        self.assertEqual(data["id"], item.id)
        self.assertEqual(data["wedding"], self.wedding.id)
        self.assertEqual(data["name"], "Buffet")
        self.assertEqual(data["category"], "FOOD")
        self.assertEqual(data["quantity"], 1)
        self.assertEqual(Decimal(data["unit_price"]), Decimal("5000.00"))
        self.assertEqual(data["status"], "PENDING")
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)

    def test_deserialization_valid(self):
        """Testa a desserialização com dados válidos."""
        data = {
            "wedding": self.wedding.id,
            "name": "DJ",
            "category": "MUSIC",
            "quantity": 1,
            "unit_price": "2500.00",
        }

        serializer = ItemSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        item = serializer.save()
        self.assertEqual(item.name, "DJ")
        self.assertEqual(item.category, "MUSIC")
        self.assertEqual(item.status, "PENDING")  # Default

    def test_validation_negative_price(self):
        """Testa validação de preço negativo."""
        data = {
            "wedding": self.wedding.id,
            "name": "Item",
            "category": "OTHERS",
            "quantity": 1,
            "unit_price": "-100.00",
        }

        serializer = ItemSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("unit_price", serializer.errors)

    def test_validation_zero_quantity(self):
        """Testa validação de quantidade zero."""
        data = {
            "wedding": self.wedding.id,
            "name": "Item",
            "category": "OTHERS",
            "quantity": 0,
            "unit_price": "100.00",
        }

        serializer = ItemSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("quantity", serializer.errors)


class ItemListSerializerTest(TestCase):
    """Testes do ItemListSerializer (otimizado para listagem)."""

    @classmethod
    def setUpTestData(cls):
        """Configuração inicial dos testes."""
        cls.user = User.objects.create_user(
            username="planner", email="planner2@example.com", password="test123"
        )
        cls.wedding = Wedding.objects.create(
            planner=cls.user,
            groom_name="Pedro",
            bride_name="Ana",
            date="2025-06-15",
            location="Rio de Janeiro",
            budget=Decimal("40000.00"),
        )

    def test_serialization_with_calculated_fields(self):
        """Testa serialização com campos calculados (total_cost, wedding_couple)."""
        item = Item.objects.create(
            wedding=self.wedding,
            name="Decoração",
            category="DECOR",
            quantity=10,
            unit_price=Decimal("150.00"),
        )

        serializer = ItemListSerializer(item)
        data = serializer.data

        self.assertEqual(data["id"], item.id)
        self.assertEqual(data["name"], "Decoração")
        self.assertEqual(data["category"], "DECOR")
        self.assertEqual(Decimal(data["total_cost"]), Decimal("1500.00"))
        self.assertEqual(data["wedding_couple"], "Pedro & Ana")

    def test_total_cost_calculation(self):
        """Testa o cálculo correto do total_cost."""
        item = Item.objects.create(
            wedding=self.wedding,
            name="Cadeiras",
            category="FURNITURE",
            quantity=50,
            unit_price=Decimal("25.50"),
        )

        serializer = ItemListSerializer(item)
        expected_total = Decimal("50") * Decimal("25.50")
        self.assertEqual(Decimal(serializer.data["total_cost"]), expected_total)


class ItemDetailSerializerTest(TestCase):
    """Testes do ItemDetailSerializer (detalhes completos)."""

    @classmethod
    def setUpTestData(cls):
        """Configuração inicial dos testes."""
        cls.user = User.objects.create_user(
            username="planner", email="planner3@example.com", password="test123"
        )
        cls.wedding = Wedding.objects.create(
            planner=cls.user,
            groom_name="Carlos",
            bride_name="Julia",
            date="2025-09-20",
            location="Belo Horizonte",
            budget=Decimal("45000.00"),
        )

    def test_serialization_with_full_details(self):
        """Testa serialização com detalhes completos."""
        item = Item.objects.create(
            wedding=self.wedding,
            name="Fotógrafo",
            category="PHOTO_VIDEO",
            quantity=1,
            unit_price=Decimal("3000.00"),
            description="Fotógrafo profissional com álbum incluso",
        )

        serializer = ItemDetailSerializer(item)
        data = serializer.data

        self.assertEqual(data["id"], item.id)
        self.assertEqual(data["name"], "Fotógrafo")
        self.assertEqual(
            data["description"], "Fotógrafo profissional com álbum incluso"
        )
        self.assertIn("contracts_count", data)
        self.assertEqual(data["contracts_count"], 0)  # Sem contratos
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)

    def test_contracts_count(self):
        """Testa a contagem de contratos associados."""
        from apps.contracts.models import Contract

        item = Item.objects.create(
            wedding=self.wedding,
            name="Banda",
            category="MUSIC",
            quantity=1,
            unit_price=Decimal("5000.00"),
        )

        # Cria 1 contrato (constraint UNIQUE no item_id)
        Contract.objects.create(item=item)

        serializer = ItemDetailSerializer(item)
        self.assertEqual(serializer.data["contracts_count"], 1)
