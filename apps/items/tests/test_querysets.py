from decimal import Decimal

from django.test import TestCase

from apps.items.models import Item
from apps.users.models import User
from apps.weddings.models import Wedding


class ItemQuerySetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("qs_user", "qs@t.com", "123")
        cls.wedding = Wedding.objects.create(
            planner=cls.user,
            groom_name="G",
            bride_name="B",
            date="2025-01-01",
            location="Loc",
            budget=50000,
        )

        # --- MOCANDO DADOS ---

        # Item 1: DECOR (Total: 2 * 50 = 100)
        cls.item1 = Item.objects.create(
            wedding=cls.wedding,
            name="Flores",
            category="DECOR",
            quantity=2,
            unit_price=Decimal("50.00"),
            status="PENDING",
        )

        # Item 2: BUFFET (Total: 1 * 300 = 300)
        cls.item2 = Item.objects.create(
            wedding=cls.wedding,
            name="Jantar",
            category="BUFFET",
            quantity=1,
            unit_price=Decimal("300.00"),
            status="DONE",
        )

        # Item 3: DECOR (Total: 10 * 5 = 50)
        # Criado para testar o agrupamento da categoria DECOR
        cls.item3 = Item.objects.create(
            wedding=cls.wedding,
            name="Velas",
            category="DECOR",
            quantity=10,
            unit_price=Decimal("5.00"),
            status="IN_PROGRESS",
        )

    def test_total_spent_calculation(self):
        """
        Deve somar (qtd * preço) de TODOS os itens.
        100 (Flores) + 300 (Jantar) + 50 (Velas) = 450.00
        """
        qs = Item.objects.all()
        total = qs.total_spent()

        self.assertIsInstance(total, Decimal)
        self.assertEqual(total, Decimal("450.00"))

    def test_total_spent_empty_queryset(self):
        """Se não houver itens, deve retornar 0 (e não None)."""
        qs = Item.objects.none()
        self.assertEqual(qs.total_spent(), 0)

    def test_category_expenses_aggregation(self):
        """
        Deve agrupar por categoria e somar os custos.
        Esperado:
        - BUFFET: 300.00
        - DECOR: 150.00 (100 das Flores + 50 das Velas)
        """
        qs = Item.objects.all().category_expenses()

        # O queryset retorna uma lista de dicts
        # Ex: [{'category': 'BUFFET', 'total_cost': 300}, ...]

        # Como ordenamos por -total_cost no manager:
        # 1º deve ser BUFFET (300)
        self.assertEqual(qs[0]["category"], "BUFFET")
        self.assertEqual(qs[0]["total_cost"], Decimal("300.00"))

        # 2º deve ser DECOR (150)
        self.assertEqual(qs[1]["category"], "DECOR")
        self.assertEqual(qs[1]["total_cost"], Decimal("150.00"))

    def test_apply_search(self):
        """Testa filtro istartswith"""
        qs = Item.objects.all()

        # Busca "Flo" -> Flores
        self.assertIn(self.item1, qs.apply_search("Flo"))
        self.assertNotIn(self.item2, qs.apply_search("Flo"))

        # Busca Vazia -> Retorna tudo
        self.assertEqual(qs.apply_search("").count(), 3)

    def test_apply_sort(self):
        """Testa ordenação mapeada."""
        qs = Item.objects.all()

        # Preço unitário decrescente: Jantar (300), Flores (50), Velas (5)
        res = qs.apply_sort("price_desc")
        self.assertEqual(res[0], self.item2)
        self.assertEqual(res[2], self.item3)

        # Fallback (id)
        res_default = qs.apply_sort("banana")
        self.assertEqual(list(res_default), list(qs.order_by("id")))

    def test_total_spent_respects_filter_chaining(self):
        """
        O cálculo total deve respeitar os filtros aplicados antes.
        Ex: Item.objects.filter(status="DONE").total_spent()
        """
        # Temos item1 (100, PENDING), item2 (300, DONE), item3 (50, IN_PROGRESS)

        # Filtra apenas os CONCLUÍDOS
        qs_done = Item.objects.filter(status="DONE")
        total = qs_done.total_spent()

        # Deve ser apenas 300, e não 450
        self.assertEqual(total, Decimal("300.00"))

    def test_apply_sort_by_status(self):
        """
        Verifica a ordem alfabética das chaves de status.
        DONE (D) < IN_PROGRESS (I) < PENDING (P)
        """
        res = Item.objects.all().apply_sort("status")

        # 1º: DONE (item2)
        self.assertEqual(res[0].status, "DONE")
        # 2º: IN_PROGRESS (item3)
        self.assertEqual(res[1].status, "IN_PROGRESS")
        # 3º: PENDING (item1)
        self.assertEqual(res[2].status, "PENDING")
