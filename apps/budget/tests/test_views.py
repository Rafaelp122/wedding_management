from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.core.constants import GRADIENTS
from apps.items.models import Item
from apps.users.models import User
from apps.weddings.models import Wedding


class BudgetPartialViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # 1. Setup Básico
        cls.user = User.objects.create_user("planner", "p@t.com", "123")
        cls.wedding = Wedding.objects.create(
            planner=cls.user,
            groom_name="G",
            bride_name="B",
            date=timezone.now().date() + timedelta(days=365),
            location="Loc",
            budget=Decimal("10000.00"),  # Orçamento de 10k
        )
        cls.url = reverse(
            "budget:partial_budget", kwargs={"wedding_id": cls.wedding.id}
        )

        # 2. Criamos Itens para popular o orçamento
        # Item 1: Buffet (Gasto alto) -> 5000.00
        Item.objects.create(
            wedding=cls.wedding,
            name="Buffet",
            category="BUFFET",
            quantity=1,
            unit_price=Decimal("5000.00"),
        )

        # Item 2: Decoração (Gasto médio) -> 2000.00
        Item.objects.create(
            wedding=cls.wedding,
            name="Flores",
            category="DECOR",
            quantity=2,
            unit_price=Decimal("1000.00"),
        )

        # Item 3: Outros (Gasto baixo) -> 500.00
        Item.objects.create(
            wedding=cls.wedding,
            name="Velas",
            category="OTHERS",
            quantity=10,
            unit_price=Decimal("50.00"),
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_financial_calculations(self):
        """
        Testa se total_spent, balance e budget estão corretos no contexto.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        context = response.context

        # Total Budget: 10.000
        self.assertEqual(context["total_budget"], Decimal("10000.00"))

        # Current Spent: 5000 + 2000 + 500 = 7500.00
        self.assertEqual(context["current_spent"], Decimal("7500.00"))

        # Available Balance: 10000 - 7500 = 2500.00
        self.assertEqual(context["available_balance"], Decimal("2500.00"))

    def test_category_distribution_logic(self):
        """
        Verifica se as categorias estão agrupadas, nomeadas corretamente e ordenadas.
        """
        response = self.client.get(self.url)
        expenses = response.context["distributed_expenses"]

        # Devemos ter 3 categorias (BUFFET, DECOR, OTHERS)
        self.assertEqual(len(expenses), 3)

        # 1º Deve ser BUFFET (5000) - Maior gasto
        self.assertEqual(expenses[0]["category"], "Buffet")  # Nome legível do choice
        self.assertEqual(expenses[0]["value"], Decimal("5000.00"))
        self.assertEqual(expenses[0]["gradient"], GRADIENTS[0])  # Primeiro gradiente

        # 2º Deve ser DECOR (2000)
        self.assertEqual(expenses[1]["category"], "Decoração")
        self.assertEqual(expenses[1]["value"], Decimal("2000.00"))

    def test_empty_state_calculations(self):
        """
        Se não houver itens, não deve quebrar e deve mostrar saldo total.
        """
        # Cria um casamento novo sem itens
        empty_w = Wedding.objects.create(
            planner=self.user,
            groom_name="Empty",
            bride_name="E",
            date=timezone.now().date(),
            location="L",
            budget=Decimal("5000.00"),
        )
        url = reverse("budget:partial_budget", kwargs={"wedding_id": empty_w.id})

        response = self.client.get(url)
        context = response.context

        self.assertEqual(context["current_spent"], 0)
        self.assertEqual(context["available_balance"], Decimal("5000.00"))
        self.assertEqual(len(context["distributed_expenses"]), 0)

    def test_security_access_control(self):
        """
        Usuário não logado -> Login.
        Usuário não dono -> 404.
        """
        # 1. Anônimo
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

        # 2. Hacker
        hacker = User.objects.create_user("hacker", "h@h.com", "123")
        self.client.force_login(hacker)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_over_budget_calculation(self):
        """
        Se os gastos superarem o orçamento, o saldo disponível deve ser negativo.
        """
        # 1. Cria um Casamento NOVO e LIMPO para este teste (Isolamento)
        # Isso evita somar com os itens criados no setUpTestData (7500.00)
        clean_wedding = Wedding.objects.create(
            planner=self.user,
            groom_name="Over",
            bride_name="Budget",
            date=timezone.now().date(),
            location="Loc",
            budget=Decimal("1000.00"),  # Orçamento Baixo
        )

        # 2. Adiciona Item Caro (1500.00) neste novo casamento
        Item.objects.create(
            wedding=clean_wedding,
            name="Extravagância",
            quantity=1,
            unit_price=Decimal("1500.00"),
        )

        # 3. Gera a URL para este casamento específico
        url = reverse("budget:partial_budget", kwargs={"wedding_id": clean_wedding.id})

        # 4. Executa a requisição
        response = self.client.get(url)
        context = response.context

        # 5. Verificações
        self.assertEqual(context["total_budget"], Decimal("1000.00"))
        self.assertEqual(
            context["current_spent"], Decimal("1500.00")
        )  # Agora será exato

        # Saldo deve ser -500.00
        self.assertEqual(context["available_balance"], Decimal("-500.00"))
