from django.test import TestCase
from django.utils import timezone

from apps.contracts.admin import ContractAdmin
from apps.contracts.models import Contract
from apps.items.models import Item
from apps.users.models import User
from apps.weddings.models import Wedding


class ContractAdminTest(TestCase):
    """Testes para métodos customizados do ContractAdmin."""

    def setUp(self):
        self.planner = User.objects.create_user("planner", "p@test.com", "123")
        self.wedding = Wedding.objects.create(
            planner=self.planner,
            groom_name="John",
            bride_name="Jane",
            date=timezone.now().date(),
            location="Location",
            budget=10000,
        )
        self.item = Item.objects.create(
            wedding=self.wedding, name="Photography", quantity=1, unit_price=3000
        )
        self.contract = Contract.objects.create(
            item=self.item, status="DRAFT", description="Photo contract"
        )
        self.admin = ContractAdmin(Contract, None)

    def test_item_name_returns_item_name(self):
        """item_name() deve retornar o nome do item."""
        result = self.admin.item_name(self.contract)
        self.assertEqual(result, "Photography")

    def test_item_name_returns_dash_when_no_item(self):
        """item_name() deve retornar '-' quando não há item."""

        # Criar mock de contrato sem item
        class MockContract:
            item = None

        mock_contract = MockContract()
        result = self.admin.item_name(mock_contract)
        self.assertEqual(result, "-")

    def test_wedding_couple_returns_couple_names(self):
        """wedding_couple() deve retornar nomes dos noivos."""
        result = self.admin.wedding_couple(self.contract)
        self.assertEqual(result, "Jane & John")

    def test_wedding_couple_returns_dash_when_no_wedding(self):
        """wedding_couple() deve retornar '-' quando não há casamento."""

        # Criar mock de contrato sem wedding
        class MockContract:
            @property
            def wedding(self):
                return None

        mock_contract = MockContract()
        result = self.admin.wedding_couple(mock_contract)
        self.assertEqual(result, "-")

    def test_supplier_name_returns_supplier(self):
        """supplier_name() deve retornar o nome do fornecedor."""
        result = self.admin.supplier_name(self.contract)
        # Item não tem supplier definido no setup, deve retornar "-"
        self.assertEqual(result, "-")

        # Adicionar supplier ao item
        self.item.supplier = "Best Photos Inc."
        self.item.save()
        self.contract.refresh_from_db()

        result = self.admin.supplier_name(self.contract)
        self.assertEqual(result, "Best Photos Inc.")

    def test_contract_value_returns_formatted_value(self):
        """contract_value() deve retornar valor formatado."""
        result = self.admin.contract_value(self.contract)
        self.assertIn("R$", result)
        self.assertIn("3,000.00", result)

    def test_signature_progress_all_unsigned(self):
        """signature_progress() com todas as assinaturas ausentes."""
        result = self.admin.signature_progress(self.contract)

        # Deve conter símbolos vazios (○) para todas as assinaturas
        self.assertIn("○ Cerimonialista", result)
        self.assertIn("○ Fornecedor", result)
        self.assertIn("○ Noivos", result)

        # Não deve conter símbolos preenchidos (✓)
        self.assertNotIn("✓ Cerimonialista", result)

    def test_signature_progress_planner_signed(self):
        """signature_progress() com apenas planner assinado."""
        self.contract.planner_signature = "signature_data"
        self.contract.save()

        result = self.admin.signature_progress(self.contract)

        self.assertIn("✓ Cerimonialista", result)
        self.assertIn("○ Fornecedor", result)
        self.assertIn("○ Noivos", result)

    def test_signature_progress_all_signed(self):
        """signature_progress() com todas as assinaturas presentes."""
        self.contract.planner_signature = "sig1"
        self.contract.supplier_signature = "sig2"
        self.contract.couple_signature = "sig3"
        self.contract.save()

        result = self.admin.signature_progress(self.contract)

        self.assertIn("✓ Cerimonialista", result)
        self.assertIn("✓ Fornecedor", result)
        self.assertIn("✓ Noivos", result)

        # Não deve conter símbolos vazios
        self.assertNotIn("○", result)

    def test_signature_progress_partial_signed(self):
        """signature_progress() com assinaturas parciais."""
        self.contract.planner_signature = "sig1"
        self.contract.couple_signature = "sig3"
        self.contract.save()

        result = self.admin.signature_progress(self.contract)

        self.assertIn("✓ Cerimonialista", result)
        self.assertIn("○ Fornecedor", result)
        self.assertIn("✓ Noivos", result)
