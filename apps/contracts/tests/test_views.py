from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.contracts.models import Contract
from apps.core.constants import GRADIENTS
from apps.items.models import Item
from apps.users.models import User
from apps.weddings.models import Wedding


class ContractsPartialViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # 1. Setup do Planner e Casamento
        cls.planner = User.objects.create_user("planner", "p@test.com", "123")
        cls.wedding = Wedding.objects.create(
            planner=cls.planner, groom_name="G", bride_name="B",
            date=timezone.now().date() + timedelta(days=365),
            location="Loc", budget=10000
        )

        # 2. Criamos Itens e Contratos
        # Criamos 3 contratos para testar a lista
        cls.contracts = []
        for i in range(3):
            item = Item.objects.create(
                wedding=cls.wedding, name=f"Item {i}",
                quantity=1, unit_price=100
            )
            contract = Contract.objects.create(item=item, status="PENDING")
            cls.contracts.append(contract)

        cls.url = reverse("contracts:partial_contracts", kwargs={"wedding_id": cls.wedding.id})

    def setUp(self):
        self.client.force_login(self.planner)

    def test_anonymous_user_redirected(self):
        """Usuário não logado vai para login."""
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)

    def test_other_planner_cannot_access(self):
        """Outro planner não pode ver os contratos deste casamento (404)."""
        other = User.objects.create_user("other", "o@test.com", "123")
        self.client.force_login(other)

        response = self.client.get(self.url)

        # O get_object_or_404(planner=request.user) garante isso
        self.assertEqual(response.status_code, 404)

    def test_view_renders_correct_template_and_context(self):
        """Acesso autorizado deve renderizar o template parcial."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "contracts/contracts_partial.html")

        # Verifica se o casamento está no contexto
        self.assertEqual(response.context["wedding"], self.wedding)

        # Verifica se a lista de contratos está presente
        self.assertIn("contracts_list", response.context)
        self.assertEqual(len(response.context["contracts_list"]), 3)

    def test_contracts_list_structure_and_gradients(self):
        """
        Verifica se a lista contém dicionários com 'contract' e 'gradient',
        e se os gradientes são atribuídos corretamente.
        """
        response = self.client.get(self.url)
        contracts_list = response.context["contracts_list"]

        # Verifica o primeiro item da lista
        first_item = contracts_list[0]
        self.assertEqual(first_item["contract"], self.contracts[0])
        self.assertEqual(first_item["gradient"], GRADIENTS[0])

        # Verifica se o segundo item pegou o segundo gradiente
        second_item = contracts_list[1]
        self.assertEqual(second_item["gradient"], GRADIENTS[1])

    def test_gradient_cycling(self):
        """
        Se houver mais contratos que cores, deve voltar para a primeira cor.
        """
        # Cria contratos extras para estourar o limite de GRADIENTS
        total_gradients = len(GRADIENTS)

        # Vamos adicionar itens até passar o total de gradientes
        extra_needed = total_gradients + 2 - len(self.contracts)

        for i in range(extra_needed):
            item = Item.objects.create(
                wedding=self.wedding, name=f"Extra {i}",
                quantity=1, unit_price=10
            )
            Contract.objects.create(item=item)

        # Faz a requisição
        response = self.client.get(self.url)
        contracts_list = response.context["contracts_list"]

        # O contrato na posição 'total_gradients' (ex: índice 5 se len=5)
        # deve ter o gradiente 0 (loop).
        loop_item = contracts_list[total_gradients]
        self.assertEqual(loop_item["gradient"], GRADIENTS[0])

    def test_view_handles_wedding_without_contracts(self):
        """
        Se o casamento não tiver contratos, deve renderizar a página normalmente
        com uma lista vazia (Empty State), sem erros.
        """
        # Criamos um casamento novo sem itens/contratos
        empty_wedding = Wedding.objects.create(
            planner=self.planner,
            groom_name="Empty", bride_name="State",
            date=timezone.now().date(), location="Nowhere", budget=0
        )

        url = reverse("contracts:partial_contracts", kwargs={"wedding_id": empty_wedding.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("contracts_list", response.context)
        self.assertEqual(len(response.context["contracts_list"]), 0)
        self.assertTemplateUsed(response, "contracts/contracts_partial.html")
