from datetime import timedelta

import pytest
from django.test import TestCase
from django.utils import timezone

from apps.contracts.models import Contract
from apps.items.models import Item
from apps.users.models import User
from apps.weddings.models import Wedding


@pytest.mark.integration
class WeddingQuerySetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="planner", email="test@test.com", password="123"
        )

        # Casamento 1: Data Futura (Em andamento)
        cls.wedding_future = Wedding.objects.create(
            planner=cls.user,
            groom_name="Future Groom",
            bride_name="Future Bride",
            date=timezone.now().date() + timedelta(days=30),
            location="Hall A",
            budget=10000,
        )

        # Casamento 2: Data Passada (Deveria ser completado automaticamente)
        cls.wedding_past = Wedding.objects.create(
            planner=cls.user,
            groom_name="Past Groom",
            bride_name="Past Bride",
            date=timezone.now().date() - timedelta(days=1),
            location="Hall B",
            budget=10000,
        )

        # Casamento 3: Cancelado explícito
        cls.wedding_canceled = Wedding.objects.create(
            planner=cls.user,
            groom_name="Canceled Groom",
            bride_name="Canceled Bride",
            date=timezone.now().date() - timedelta(days=10),  # Passado, mas cancelado
            location="Hall C",
            budget=10000,
            status="CANCELED",
        )

    def test_apply_search(self):
        """
        Testa se a busca (istartswith) funciona para noivo ou noiva.
        """
        qs = Wedding.objects.all()

        # Busca pelo início do nome do noivo "Fut" -> Future Groom
        res1 = qs.apply_search("Fut")
        self.assertIn(self.wedding_future, res1)
        self.assertNotIn(self.wedding_past, res1)

        # Busca pelo início do nome da noiva "Pas" -> Past Bride
        res2 = qs.apply_search("Pas")
        self.assertIn(self.wedding_past, res2)

        # Busca que não existe
        res3 = qs.apply_search("NonExistent")
        self.assertFalse(res3.exists())

    def test_apply_sort(self):
        """
        Testa a ordenação mapeada.
        """
        qs = Wedding.objects.all()

        # Data Descendente (Mais futuro pro passado)
        res_desc = qs.apply_sort("date_desc")
        self.assertEqual(res_desc.first(), self.wedding_future)

        # Data Ascendente (Passado pro futuro)
        # Nota: wedding_canceled é o mais antigo (hoje - 10 dias)
        res_asc = qs.apply_sort("date_asc")
        self.assertEqual(res_asc.first(), self.wedding_canceled)

        # Nome Ascendente (Canceled, Future, Past)
        res_name = qs.apply_sort("name_asc")
        self.assertEqual(res_name.first(), self.wedding_canceled)
        self.assertEqual(res_name.last(), self.wedding_past)

    def test_with_effective_status(self):
        """
        Testa a lógica de Case/When para status baseado em data.
        """
        qs = Wedding.objects.all().with_effective_status()

        # Casamento futuro e status IN_PROGRESS -> Mantém IN_PROGRESS
        w_future = qs.get(pk=self.wedding_future.pk)
        self.assertEqual(w_future.effective_status, "IN_PROGRESS")

        # Casamento passado e status IN_PROGRESS -> Vira COMPLETED
        w_past = qs.get(pk=self.wedding_past.pk)
        self.assertEqual(w_past.effective_status, "COMPLETED")

        # Casamento passado mas status CANCELED -> Mantém CANCELED
        w_canceled = qs.get(pk=self.wedding_canceled.pk)
        self.assertEqual(w_canceled.effective_status, "CANCELED")

    def test_with_counts_and_progress(self):
        """
        Testa as anotações de contagem (items, done_items, contracts) e progresso.
        """
        # --- SETUP DOS ITENS PARA O TESTE ---
        # Cria 4 itens para o Casamento Futuro
        # Item 1: Feito
        item1 = Item.objects.create(
            wedding=self.wedding_future,
            name="Item 1",
            status="DONE",
            quantity=1,
            unit_price=10.0,
        )
        # Item 2: Pendente
        _item2 = Item.objects.create(
            wedding=self.wedding_future,
            name="Item 2",
            status="PENDING",
            quantity=1,
            unit_price=10.0,
        )
        # Item 3: Feito
        _item3 = Item.objects.create(
            wedding=self.wedding_future,
            name="Item 3",
            status="DONE",
            quantity=1,
            unit_price=10.0,
        )
        # Item 4: Pendente
        _item4 = Item.objects.create(
            wedding=self.wedding_future,
            name="Item 4",
            status="PENDING",
            quantity=1,
            unit_price=10.0,
        )

        # Cria 1 Contrato vinculado ao Item 1
        Contract.objects.create(
            item=item1,
            description="Contrato de prestação de serviços",
        )

        # --- EXECUÇÃO ---
        qs = Wedding.objects.filter(
            pk=self.wedding_future.pk
        ).with_counts_and_progress()
        wedding = qs.first()

        # --- VERIFICAÇÃO ---
        # Total Itens: 4
        self.assertEqual(wedding.items_count, 4)

        # Itens Feitos (DONE): 2
        self.assertEqual(wedding.done_items_count, 2)

        # Total Contratos: 1
        self.assertEqual(wedding.contracts_count, 1)

        # Progresso: 2 feitos de 4 total = 50%
        self.assertEqual(wedding.progress, 50)

    def test_progress_calculation_division_by_zero(self):
        """
        Garante que casamentos sem itens tenham progresso 0 e não quebrem
        (divisão por zero).
        """
        qs = Wedding.objects.filter(pk=self.wedding_past.pk).with_counts_and_progress()
        wedding = qs.first()

        self.assertEqual(wedding.items_count, 0)
        self.assertEqual(wedding.progress, 0)

    def test_apply_sort_invalid_option_defaults_to_id(self):
        """
        Se passar uma opção de ordenação desconhecida (ex: lixo na URL),
        deve cair no default 'id' (ordem de criação).
        """
        qs = Wedding.objects.all()

        # Ordenação por ID crescente (default):
        # 1. Future (criado primeiro no setUp)
        # 2. Past
        # 3. Canceled

        res = qs.apply_sort("banana_split")  # Opção inválida

        # Deve manter a ordem padrão (ID)
        self.assertEqual(res.first(), self.wedding_future)
        self.assertEqual(res.last(), self.wedding_canceled)

    def test_with_effective_status_manual_completion_priority(self):
        """
        Se o usuário marcar 'COMPLETED' manualmente, isso deve prevalecer
        mesmo que a data seja futura (ex: adiantou o casamento).
        """
        # Cria um casamento no FUTURO, mas marcado como COMPLETED
        w_early_finish = Wedding.objects.create(
            planner=self.user,
            groom_name="Early Groom",
            bride_name="Early Bride",
            date=timezone.now().date() + timedelta(days=50),  # Futuro
            location="Hall D",
            budget=10000,
            status="COMPLETED",  # Manualmente concluído
        )

        qs = Wedding.objects.filter(pk=w_early_finish.pk).with_effective_status()
        wedding = qs.first()

        # Não deve ser IN_PROGRESS (pela data), deve ser COMPLETED (pelo status)
        self.assertEqual(wedding.effective_status, "COMPLETED")
