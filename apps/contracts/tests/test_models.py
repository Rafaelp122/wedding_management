from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from apps.contracts.models import Contract
from apps.items.models import Item
from apps.users.models import User
from apps.weddings.models import Wedding


class ContractModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Cria a cadeia de dependências
        cls.user = User.objects.create_user("c_user", "c@t.com", "123")
        cls.wedding = Wedding.objects.create(
            planner=cls.user, groom_name="G", bride_name="B",
            date="2025-01-01", location="Loc", budget=1000
        )
        cls.item = Item.objects.create(
            wedding=cls.wedding, name="Fotógrafo", 
            quantity=1, unit_price=5000, supplier="Foto Studio X"
        )

    def test_contract_creation_and_str(self):
        """Verifica criação básica e representação em string."""
        contract = Contract.objects.create(item=self.item, status="PENDING")

        self.assertEqual(str(contract), "Contrato: Fotógrafo")
        self.assertEqual(contract.status, "PENDING")

    def test_property_delegation(self):
        """
        Verifica se as properties .supplier e .wedding pegam os dados do Item corretamente.
        """
        contract = Contract.objects.create(item=self.item)

        # Deve vir do item
        self.assertEqual(contract.supplier, "Foto Studio X")
        self.assertEqual(contract.wedding, self.wedding)

    def test_date_validation_logic(self):
        """
        A data de expiração não pode ser menor que a assinatura.
        """
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)

        contract = Contract(
            item=self.item,
            signature_date=today,
            expiration_date=yesterday  # Inválido!
        )

        with self.assertRaises(ValidationError) as cm:
            contract.full_clean()  # Dispara o .clean()

        self.assertIn("expiration_date", cm.exception.message_dict)

    def test_date_validation_success(self):
        """
        Datas válidas (assinatura <= expiração) devem passar.
        """
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)

        contract = Contract(
            item=self.item,
            signature_date=today,
            expiration_date=tomorrow  # Válido
        )
        # Não deve lançar erro
        contract.full_clean()

    def test_item_deletion_cascades_to_contract(self):
        """
        Se o Item for deletado, o Contrato deve ser deletado automaticamente.
        """
        contract = Contract.objects.create(item=self.item)
        contract_pk = contract.pk

        # Deleta o item (pai)
        self.item.delete()

        # Verifica se o contrato (filho) sumiu
        self.assertFalse(Contract.objects.filter(pk=contract_pk).exists())

    def test_reverse_access_from_item(self):
        """
        Deve ser possível acessar o contrato através do item (related_name='contract').
        """
        contract = Contract.objects.create(item=self.item)

        # Refresh no item para o Django carregar a relação
        self.item.refresh_from_db()

        self.assertEqual(self.item.contract, contract)

    def test_one_to_one_constraint(self):
        """
        Não deve ser possível criar dois contratos para o mesmo item.
        Isso deve gerar um erro de integridade no banco.
        """
        from django.db.utils import IntegrityError

        # Cria o primeiro
        Contract.objects.create(item=self.item)

        # Tenta criar o segundo para o mesmo item
        with self.assertRaises(IntegrityError):
            Contract.objects.create(item=self.item)
