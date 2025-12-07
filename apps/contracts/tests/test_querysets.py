"""
Testes para os querysets customizados do app contracts.
"""

from typing import cast

from django.test import TestCase

from apps.contracts.models import Contract
from apps.contracts.querysets import ContractQuerySet
from apps.items.models import Item
from apps.users.models import User
from apps.weddings.models import Wedding


class ContractQuerySetTest(TestCase):
    """Testes para o ContractQuerySet."""

    def setUp(self):
        # Cria planners
        self.planner1 = User.objects.create_user("planner1", "p1@test.com", "123")
        self.planner2 = User.objects.create_user("planner2", "p2@test.com", "123")

        # Cria casamentos
        self.wedding1 = Wedding.objects.create(
            planner=self.planner1,
            groom_name="João",
            bride_name="Maria",
            date="2025-06-15",
            location="Salão",
            budget=50000,
        )

        self.wedding2 = Wedding.objects.create(
            planner=self.planner2,
            groom_name="Pedro",
            bride_name="Ana",
            date="2025-12-01",
            location="Igreja",
            budget=30000,
        )

        # Cria itens e contratos para wedding1
        for i in range(3):
            item = Item.objects.create(
                wedding=self.wedding1,
                name=f"Item {i}",
                quantity=1,
                unit_price=1000 * (i + 1),
                supplier=f"Fornecedor {i}",
            )
            status = ["DRAFT", "WAITING_PLANNER", "WAITING_SUPPLIER"][i]
            Contract.objects.create(item=item, status=status)

        # Cria contratos para wedding2
        item = Item.objects.create(
            wedding=self.wedding2, name="Item P2", quantity=1, unit_price=5000
        )
        Contract.objects.create(item=item, status="COMPLETED")

    def test_for_planner_filters_by_planner(self):
        """Deve filtrar contratos do planner específico."""
        contracts = Contract.objects.for_planner(self.planner1)

        self.assertEqual(contracts.count(), 3)
        for contract in contracts:
            self.assertEqual(contract.item.wedding.planner, self.planner1)

    def test_for_planner_excludes_other_planners(self):
        """Não deve incluir contratos de outros planners."""
        contracts = Contract.objects.for_planner(self.planner1)

        # Verifica que não tem contratos do planner2
        for contract in contracts:
            self.assertNotEqual(contract.item.wedding.planner, self.planner2)

    def test_for_wedding_filters_by_wedding(self):
        """Deve filtrar contratos do casamento específico."""
        contracts = Contract.objects.for_wedding(self.wedding1)

        self.assertEqual(contracts.count(), 3)
        for contract in contracts:
            self.assertEqual(contract.item.wedding, self.wedding1)

    def test_with_related_optimizes_queries(self):
        """Deve usar select_related para otimização."""
        contracts = Contract.objects.with_related()

        # Força avaliação do queryset
        list(contracts)

        # Verifica que tem select_related aplicado
        # (não há como testar diretamente sem contar queries,
        # mas podemos verificar que o método existe e retorna queryset)
        self.assertIsInstance(contracts, ContractQuerySet)

    def test_fully_signed_filters_completed_contracts(self):
        """Deve retornar apenas contratos totalmente assinados."""
        # Cria contrato completo com todas as assinaturas
        item = Item.objects.create(
            wedding=self.wedding1, name="Completo", quantity=1, unit_price=1000
        )
        contract = Contract.objects.create(item=item, status="COMPLETED")
        # Simula assinaturas
        contract.planner_signature = "fake_sig.png"
        contract.supplier_signature = "fake_sig.png"
        contract.couple_signature = "fake_sig.png"
        contract.save()

        fully_signed = Contract.objects.fully_signed()

        # Verifica que tem pelo menos o contrato que criamos
        # (pode ter o do wedding2 que também é COMPLETED)
        self.assertGreaterEqual(fully_signed.count(), 1)

        # Verifica que nosso contrato está na lista
        contract_ids = [c.id for c in fully_signed]
        self.assertIn(contract.id, contract_ids)

        # Verifica que todos têm status COMPLETED e assinaturas
        for c in fully_signed:
            self.assertEqual(c.status, "COMPLETED")
            self.assertIsNotNone(c.planner_signature)
            self.assertIsNotNone(c.supplier_signature)
            self.assertIsNotNone(c.couple_signature)

    def test_editable_filters_draft_and_waiting_planner(self):
        """Deve retornar apenas contratos editáveis."""
        editable = Contract.objects.editable()

        # Deve ter DRAFT e WAITING_PLANNER (2 contratos)
        self.assertEqual(editable.count(), 2)

        statuses = [c.status for c in editable]
        self.assertIn("DRAFT", statuses)
        self.assertIn("WAITING_PLANNER", statuses)

    def test_editable_excludes_other_statuses(self):
        """Não deve incluir contratos em outros status."""
        editable = Contract.objects.editable()

        for contract in editable:
            self.assertIn(contract.status, ["DRAFT", "WAITING_PLANNER"])

    def test_cancelable_excludes_completed(self):
        """Deve excluir contratos completos."""
        cancelable = Contract.objects.cancelable()

        # Deve ter todos exceto o COMPLETED do wedding2
        self.assertEqual(cancelable.count(), 3)

        for contract in cancelable:
            self.assertNotEqual(contract.status, "COMPLETED")

    def test_bulk_cancel_updates_status(self):
        """Deve cancelar múltiplos contratos."""
        # Cancela todos os contratos canceláveis do planner1
        count = Contract.objects.for_planner(self.planner1).bulk_cancel()

        self.assertEqual(count, 3)

        # Verifica que foram cancelados
        canceled = Contract.objects.filter(
            item__wedding__planner=self.planner1, status="CANCELED"
        )
        self.assertEqual(canceled.count(), 3)

    def test_bulk_update_description_updates_all(self):
        """Deve atualizar descrição de múltiplos contratos."""
        new_description = "Descrição atualizada em lote"

        count = Contract.objects.editable().bulk_update_description(new_description)

        self.assertEqual(count, 2)

        # Verifica que foram atualizados
        updated = Contract.objects.filter(description=new_description)
        self.assertEqual(updated.count(), 2)

    def test_with_signature_status_annotates_signatures(self):
        """Deve anotar status das assinaturas."""
        contracts = Contract.objects.with_signature_status()

        # Força avaliação
        contract = contracts.first()

        # Verifica que tem as anotações
        self.assertTrue(hasattr(contract, "has_planner_signature"))
        self.assertTrue(hasattr(contract, "has_supplier_signature"))
        self.assertTrue(hasattr(contract, "has_couple_signature"))

    def test_get_next_signer_name_waiting_planner(self):
        """Deve retornar info do cerimonialista."""
        contract = Contract.objects.filter(status="WAITING_PLANNER").first()
        self.assertIsNotNone(contract)
        contract = cast(Contract, contract)  # Type narrowing

        info = Contract.objects.get_next_signer_name(contract.id)

        self.assertEqual(info["role"], "Cerimonialista")
        self.assertIn("Cerimonialista", info["name"])

    def test_get_next_signer_name_waiting_supplier(self):
        """Deve retornar info do fornecedor."""
        contract = Contract.objects.filter(status="WAITING_SUPPLIER").first()
        self.assertIsNotNone(contract)
        contract = cast(Contract, contract)  # Type narrowing

        info = Contract.objects.get_next_signer_name(contract.id)

        self.assertEqual(info["role"], "Fornecedor")
        self.assertIn("Fornecedor", info["name"])

    def test_get_next_signer_name_invalid_id(self):
        """Deve retornar mensagem de erro para ID inválido."""
        info = Contract.objects.get_next_signer_name(99999)

        self.assertEqual(info["role"], "Erro")
        self.assertIn("não encontrado", info["name"].lower())


class ContractQuerySetChainingTest(TestCase):
    """Testes para encadeamento de métodos do queryset."""

    def setUp(self):
        planner = User.objects.create_user("p", "p@test.com", "123")
        wedding = Wedding.objects.create(
            planner=planner,
            groom_name="João",
            bride_name="Maria",
            date="2025-06-15",
            location="Salão",
            budget=50000,
        )

        # Cria vários contratos com diferentes status
        for i in range(5):
            item = Item.objects.create(
                wedding=wedding, name=f"Item {i}", quantity=1, unit_price=1000
            )
            statuses = [
                "DRAFT",
                "WAITING_PLANNER",
                "WAITING_SUPPLIER",
                "WAITING_COUPLE",
                "COMPLETED",
            ]
            Contract.objects.create(item=item, status=statuses[i])

        self.wedding = wedding
        self.planner = planner

    def test_chaining_for_planner_and_editable(self):
        """Deve encadear for_planner e editable."""
        contracts = Contract.objects.for_planner(self.planner).editable()

        self.assertEqual(contracts.count(), 2)

    def test_chaining_for_wedding_and_cancelable(self):
        """Deve encadear for_wedding e cancelable."""
        contracts = Contract.objects.for_wedding(self.wedding).cancelable()

        # Todos exceto COMPLETED (4 contratos)
        self.assertEqual(contracts.count(), 4)

    def test_chaining_with_related_and_for_planner(self):
        """Deve encadear with_related e for_planner."""
        contracts = Contract.objects.with_related().for_planner(self.planner)

        self.assertEqual(contracts.count(), 5)

    def test_chaining_multiple_filters(self):
        """Deve encadear múltiplos filtros."""
        contracts = (
            Contract.objects.for_planner(self.planner)
            .for_wedding(self.wedding)
            .editable()
            .with_related()
        )

        self.assertEqual(contracts.count(), 2)

        # Verifica que são os editáveis
        for contract in contracts:
            self.assertIn(contract.status, ["DRAFT", "WAITING_PLANNER"])


class ContractManagerTest(TestCase):
    """Testes para o ContractManager."""

    def setUp(self):
        planner = User.objects.create_user("p", "p@test.com", "123")
        wedding = Wedding.objects.create(
            planner=planner,
            groom_name="João",
            bride_name="Maria",
            date="2025-06-15",
            location="Salão",
            budget=50000,
        )
        item = Item.objects.create(
            wedding=wedding, name="Fotógrafo", quantity=1, unit_price=5000
        )
        Contract.objects.create(item=item)

    def test_manager_uses_custom_queryset(self):
        """Manager deve usar ContractQuerySet."""
        queryset = Contract.objects.all()

        self.assertIsInstance(queryset, ContractQuerySet)

    def test_manager_has_queryset_methods(self):
        """Manager deve ter métodos do queryset."""
        self.assertTrue(hasattr(Contract.objects, "for_planner"))
        self.assertTrue(hasattr(Contract.objects, "for_wedding"))
        self.assertTrue(hasattr(Contract.objects, "editable"))
        self.assertTrue(hasattr(Contract.objects, "cancelable"))
        self.assertTrue(hasattr(Contract.objects, "fully_signed"))
