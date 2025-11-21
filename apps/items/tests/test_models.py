from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
from apps.items.models import Item
from apps.weddings.models import Wedding
from apps.users.models import User


class ItemModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Setup básico para não dar erro de FK se tiver
        cls.user = User.objects.create_user("u", "u@t.com", "123")
        cls.wedding = Wedding.objects.create(
            planner=cls.user,
            groom_name="G", bride_name="B",
            date="2025-01-01", location="Loc", budget=1000
        )

    def test_total_cost_property(self):
        """
        A property .total_cost deve multiplicar quantidade * preço unitário.
        """
        item = Item(quantity=5, unit_price=Decimal('20.00'))
        # 5 * 20.00 = 100.00
        self.assertEqual(item.total_cost, Decimal('100.00'))

    def test_str_representation(self):
        item = Item(name="Cadeira Tiffany")
        self.assertEqual(str(item), "Cadeira Tiffany")

    def test_quantity_must_be_positive(self):
        """
        Garante que quantidade não pode ser negativa
        (Se você aplicou PositiveIntegerField).
        """
        item = Item(
            name="Teste", quantity=-1, unit_price=10,
            wedding=self.wedding
        )
        # O Django valida PositiveInteger no nível do banco ou full_clean
        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_unit_price_cannot_be_negative(self):
        """
        Garante que preço não pode ser negativo
        (Se você aplicou o MinValueValidator).
        """
        item = Item(
            name="Teste", quantity=1, unit_price=Decimal("-10.00"),
            wedding=self.wedding
        )
        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_wedding_deletion_cascades(self):
        """
        Se o Casamento for deletado, o Item deve ser deletado junto.
        (Garante integridade do on_delete=models.CASCADE)
        """
        # Cria um item vinculado ao casamento do setUp
        item = Item.objects.create(
            name="Item Cascata", quantity=1, unit_price=10,
            wedding=self.wedding
        )

        # Deleta o casamento
        self.wedding.delete()

        # O item deve ter sumido
        self.assertFalse(Item.objects.filter(pk=item.pk).exists())
