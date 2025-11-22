import base64
from datetime import timedelta
from io import BytesIO

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from PIL import Image

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


class GenerateSignatureLinkViewTest(TestCase):
    """Testes para a view que gera links de assinatura."""

    def setUp(self):
        self.planner = User.objects.create_user("planner", "p@t.com", "123")
        self.wedding = Wedding.objects.create(
            planner=self.planner,
            groom_name="Carlos",
            bride_name="Lucia",
            date=timezone.now().date() + timedelta(days=90),
            location="Hotel",
            budget=40000
        )
        self.item = Item.objects.create(
            wedding=self.wedding,
            name="Banda",
            quantity=1,
            unit_price=8000,
            supplier="Música Viva"
        )
        self.contract = Contract.objects.create(
            item=self.item,
            status="WAITING_PLANNER"
        )
        self.url = reverse(
            "contracts:generate_link",
            kwargs={"contract_id": self.contract.id}
        )
        self.client.force_login(self.planner)

    def test_anonymous_user_redirected(self):
        """Usuário não logado deve ser redirecionado."""
        self.client.logout()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)

    def test_generates_link_successfully(self):
        """Deve gerar link de assinatura com sucesso."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn("link", data)
        self.assertIn("status", data)
        self.assertIn("message", data)
        self.assertIn(str(self.contract.token), data["link"])

    def test_message_shows_next_signer(self):
        """Mensagem deve indicar o próximo assinante."""
        response = self.client.get(self.url)
        data = response.json()

        self.assertIn("Cerimonialista", data["message"])

    def test_message_for_supplier_status(self):
        """Status WAITING_SUPPLIER deve mostrar fornecedor."""
        self.contract.status = "WAITING_SUPPLIER"
        self.contract.save()

        response = self.client.get(self.url)
        data = response.json()

        self.assertIn("Fornecedor", data["message"])
        self.assertIn("Música Viva", data["message"])


class SignContractExternalViewTest(TestCase):
    """Testes para a view pública de assinatura de contratos."""

    def setUp(self):
        self.planner = User.objects.create_user("planner", "p@t.com", "123")
        self.wedding = Wedding.objects.create(
            planner=self.planner,
            groom_name="Roberto",
            bride_name="Fernanda",
            date=timezone.now().date() + timedelta(days=120),
            location="Praia",
            budget=60000
        )
        self.item = Item.objects.create(
            wedding=self.wedding,
            name="Catering",
            quantity=1,
            unit_price=15000,
            supplier="Buffet Premium"
        )
        self.contract = Contract.objects.create(
            item=self.item,
            status="WAITING_PLANNER"
        )
        self.url = reverse(
            "contracts:sign_contract",
            kwargs={"token": self.contract.token}
        )

    def _create_fake_signature_base64(self):
        """Helper para criar assinatura base64 fake."""
        img = Image.new('RGB', (100, 50), color='white')
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_bytes = buffer.getvalue()
        img_b64 = base64.b64encode(img_bytes).decode('utf-8')
        return f"data:image/png;base64,{img_b64}"

    def test_anonymous_user_can_access(self):
        """Acesso público deve ser permitido (sem login)."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "contracts/external_signature.html"
        )

    def test_context_contains_contract_and_role(self):
        """Contexto deve conter contrato e papel do assinante."""
        response = self.client.get(self.url)

        self.assertIn("contract", response.context)
        self.assertIn("signer_role", response.context)
        self.assertEqual(
            response.context["signer_role"],
            "Cerimonialista"
        )

    def test_post_without_signature_shows_error(self):
        """POST sem assinatura deve mostrar erro."""
        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertIn("error", response.context)
        self.assertIn("desenhe sua assinatura", response.context["error"])

    def test_post_with_valid_signature_processes_successfully(self):
        """POST com assinatura válida deve processar."""
        sig = self._create_fake_signature_base64()

        response = self.client.post(
            self.url,
            {"signature_base64": sig},
            HTTP_X_FORWARDED_FOR="203.0.113.1"
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "contracts/signature_success.html")

        # Verifica se processou
        self.contract.refresh_from_db()
        self.assertEqual(self.contract.status, "WAITING_SUPPLIER")
        self.assertIsNotNone(self.contract.planner_signature)

    def test_completed_contract_shows_success_page(self):
        """Contrato completo deve mostrar página de sucesso."""
        self.contract.status = "COMPLETED"
        self.contract.integrity_hash = "abc123"
        self.contract.save()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Finalizado")


class DownloadContractPDFViewTest(TestCase):
    """Testes para a view de download de PDF."""

    def setUp(self):
        self.planner = User.objects.create_user("planner", "p@t.com", "123")
        self.other_user = User.objects.create_user("other", "o@t.com", "123")

        self.wedding = Wedding.objects.create(
            planner=self.planner,
            groom_name="Marcos",
            bride_name="Paula",
            date=timezone.now().date() + timedelta(days=60),
            location="Fazenda",
            budget=70000
        )
        self.item = Item.objects.create(
            wedding=self.wedding,
            name="Fotografia",
            quantity=1,
            unit_price=6000,
            supplier="Click Photos"
        )
        self.contract = Contract.objects.create(
            item=self.item,
            status="COMPLETED",
            integrity_hash="abc123def456"
        )
        self.url = reverse(
            "contracts:download_pdf",
            kwargs={"contract_id": self.contract.id}
        )

    def test_anonymous_user_redirected_to_login(self):
        """Usuário não logado deve ser redirecionado."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)

    def test_other_user_receives_403(self):
        """Outro usuário não pode baixar o contrato."""
        self.client.force_login(self.other_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_owner_can_download_pdf(self):
        """Proprietário pode baixar o PDF."""
        self.client.force_login(self.planner)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn('contrato_', response['Content-Disposition'])

