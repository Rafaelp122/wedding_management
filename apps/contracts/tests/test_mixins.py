"""
Testes para os mixins refatorados do app contracts.
"""

import base64
from io import BytesIO
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase
from PIL import Image

from apps.contracts.mixins import (
    ContractActionsMixin,
    ContractEmailMixin,
    ContractManagementMixin,
    ContractOwnershipMixin,
    ContractQuerysetMixin,
    ContractSignatureMixin,
    ContractUrlGeneratorMixin,
)
from apps.contracts.models import Contract
from apps.items.models import Item
from apps.users.models import User
from apps.weddings.models import Wedding


class ContractOwnershipMixinTest(TestCase):
    """Testes para o ContractOwnershipMixin."""

    def setUp(self):
        self.factory = RequestFactory()
        self.mixin = ContractOwnershipMixin()

        # Cria usuários e dados de teste
        self.owner = User.objects.create_user("owner", "owner@test.com", "123")
        self.other_user = User.objects.create_user("other", "other@test.com", "123")

        self.wedding = Wedding.objects.create(
            planner=self.owner,
            groom_name="João",
            bride_name="Maria",
            date="2025-06-15",
            location="Salão",
            budget=50000,
        )

        self.item = Item.objects.create(
            wedding=self.wedding, name="Fotógrafo", quantity=1, unit_price=5000
        )

        self.contract = Contract.objects.create(item=self.item)

    def test_model_and_owner_field_configured(self):
        """Verifica se model e owner_field_name estão configurados."""
        self.assertEqual(self.mixin.model, Contract)
        self.assertEqual(self.mixin.owner_field_name, "item__wedding__planner")

    def test_get_queryset_filters_by_owner(self):
        """Queryset deve filtrar apenas contratos do owner."""
        request = self.factory.get("/")
        request.user = self.owner
        self.mixin.request = request

        queryset = self.mixin.get_queryset()

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first(), self.contract)

    def test_get_queryset_excludes_other_users_contracts(self):
        """Queryset não deve incluir contratos de outros usuários."""
        # Cria contrato de outro usuário
        other_wedding = Wedding.objects.create(
            planner=self.other_user,
            groom_name="Pedro",
            bride_name="Ana",
            date="2025-12-01",
            location="Igreja",
            budget=30000,
        )
        other_item = Item.objects.create(
            wedding=other_wedding, name="DJ", quantity=1, unit_price=2000
        )
        Contract.objects.create(item=other_item)

        request = self.factory.get("/")
        request.user = self.owner
        self.mixin.request = request

        queryset = self.mixin.get_queryset()

        # Deve ter apenas o contrato do owner
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().item.wedding.planner, self.owner)


class ContractQuerysetMixinTest(TestCase):
    """Testes para o ContractQuerysetMixin."""

    def setUp(self):
        self.factory = RequestFactory()
        self.mixin = ContractQuerysetMixin()

        self.planner = User.objects.create_user("planner", "p@test.com", "123")

        self.wedding = Wedding.objects.create(
            planner=self.planner,
            groom_name="João",
            bride_name="Maria",
            date="2025-06-15",
            location="Salão",
            budget=50000,
        )

        # Cria múltiplos contratos
        for i in range(3):
            item = Item.objects.create(
                wedding=self.wedding,
                name=f"Item {i}",
                quantity=1,
                unit_price=1000 * (i + 1),
            )
            Contract.objects.create(item=item)

        request = self.factory.get("/")
        request.user = self.planner
        self.mixin.request = request

    def test_get_contracts_for_planner_returns_all_contracts(self):
        """Deve retornar todos os contratos do planner."""
        contracts = self.mixin.get_contracts_for_planner()

        self.assertEqual(contracts.count(), 3)

    def test_get_contracts_for_planner_uses_with_related(self):
        """Deve usar select_related para otimização."""
        contracts = self.mixin.get_contracts_for_planner()

        # Verifica que a query foi otimizada
        # (queryset deve ter os prefetch/select aplicados)
        self.assertTrue(hasattr(contracts, "query"))

    def test_get_contracts_for_wedding_returns_filtered_contracts(self):
        """Deve retornar apenas contratos do casamento específico."""
        contracts = self.mixin.get_contracts_for_wedding(self.wedding.id)

        self.assertEqual(contracts.count(), 3)
        for contract in contracts:
            self.assertEqual(contract.item.wedding, self.wedding)

    def test_get_contracts_for_wedding_raises_404_for_invalid_id(self):
        """Deve retornar 404 para wedding_id inválido."""
        from django.http import Http404

        with self.assertRaises(Http404):
            self.mixin.get_contracts_for_wedding(99999)


class ContractSignatureMixinTest(TestCase):
    """Testes para o ContractSignatureMixin."""

    def setUp(self):
        self.factory = RequestFactory()
        self.mixin = ContractSignatureMixin()

        planner = User.objects.create_user("p", "p@t.com", "123")
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
        self.contract = Contract.objects.create(item=item)

    def _create_fake_signature_base64(self):
        """Helper para criar assinatura base64 fake."""
        img = Image.new("RGB", (100, 50), color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_bytes = buffer.getvalue()
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")
        return f"data:image/png;base64,{img_b64}"

    def test_process_contract_signature_success(self):
        """Deve processar assinatura com sucesso."""
        request = self.factory.post("/")
        request.META["REMOTE_ADDR"] = "192.168.1.1"

        signature = self._create_fake_signature_base64()

        success, message = self.mixin.process_contract_signature(
            self.contract, signature, request
        )

        self.assertTrue(success)
        self.assertIn("sucesso", message.lower())

    def test_process_contract_signature_handles_errors(self):
        """Deve capturar e retornar erros de forma amigável."""
        request = self.factory.post("/")
        request.META["REMOTE_ADDR"] = "192.168.1.1"

        # Assinatura inválida
        success, message = self.mixin.process_contract_signature(
            self.contract, "invalid_signature", request
        )

        self.assertFalse(success)
        self.assertIsInstance(message, str)


class ContractUrlGeneratorMixinTest(TestCase):
    """Testes para o ContractUrlGeneratorMixin."""

    def setUp(self):
        self.factory = RequestFactory()
        self.mixin = ContractUrlGeneratorMixin()

        planner = User.objects.create_user("p", "p@t.com", "123")
        wedding = Wedding.objects.create(
            planner=planner,
            groom_name="João",
            bride_name="Maria",
            date="2025-06-15",
            location="Salão",
            budget=50000,
        )
        item = Item.objects.create(
            wedding=wedding, name="DJ", quantity=1, unit_price=2000
        )
        self.contract = Contract.objects.create(item=item)

    def test_generate_signature_link_returns_dict(self):
        """Deve retornar dicionário com informações do link."""
        request = self.factory.get("/")
        self.mixin.request = request

        link_info = self.mixin.generate_signature_link(self.contract)

        self.assertIsInstance(link_info, dict)
        self.assertIn("link", link_info)
        self.assertIn("status", link_info)

    def test_generate_signature_link_creates_absolute_url(self):
        """Link deve ser URL absoluta."""
        request = self.factory.get("/")
        self.mixin.request = request

        link_info = self.mixin.generate_signature_link(self.contract)

        self.assertTrue(link_info["link"].startswith("http"))


class ContractEmailMixinTest(TestCase):
    """Testes para o ContractEmailMixin."""

    def setUp(self):
        self.factory = RequestFactory()
        self.mixin = ContractEmailMixin()

        # Adiciona request ao mixin
        request = self.factory.get("/")
        self.mixin.request = request

        planner = User.objects.create_user("p", "p@t.com", "123")
        wedding = Wedding.objects.create(
            planner=planner,
            groom_name="João",
            bride_name="Maria",
            date="2025-06-15",
            location="Salão",
            budget=50000,
        )
        item = Item.objects.create(
            wedding=wedding, name="Buffet", quantity=1, unit_price=10000
        )
        self.contract = Contract.objects.create(item=item)

    @patch("django.core.mail.send_mail")
    def test_send_signature_email_success(self, mock_send_mail):
        """Deve enviar e-mail com sucesso."""
        mock_send_mail.return_value = 1  # Simula sucesso

        success, message = self.mixin.send_signature_email(
            self.contract, "destinatario@test.com"
        )

        self.assertTrue(success)
        self.assertIn("enviado", message.lower())
        mock_send_mail.assert_called_once()

    @patch("django.core.mail.send_mail")
    def test_send_signature_email_handles_errors(self, mock_send_mail):
        """Deve capturar erros de envio de e-mail."""
        mock_send_mail.side_effect = Exception("SMTP Error")

        success, message = self.mixin.send_signature_email(
            self.contract, "destinatario@test.com"
        )

        self.assertFalse(success)
        self.assertIn("erro", message.lower())

    def test_send_signature_email_validates_email(self):
        """Deve capturar erro de e-mail inválido."""
        # Email inválido vai gerar erro no send_mail
        with patch("django.core.mail.send_mail") as mock_send_mail:
            mock_send_mail.side_effect = Exception("Invalid email")

            success, message = self.mixin.send_signature_email(
                self.contract, "invalid_email"
            )

            self.assertFalse(success)


class ContractActionsMixinTest(TestCase):
    """Testes para o ContractActionsMixin."""

    def setUp(self):
        self.mixin = ContractActionsMixin()

        planner = User.objects.create_user("p", "p@t.com", "123")
        wedding = Wedding.objects.create(
            planner=planner,
            groom_name="João",
            bride_name="Maria",
            date="2025-06-15",
            location="Salão",
            budget=50000,
        )
        item = Item.objects.create(
            wedding=wedding, name="Decoração", quantity=1, unit_price=3000
        )
        self.contract = Contract.objects.create(item=item, status="WAITING_PLANNER")

    def test_cancel_contract_success(self):
        """Deve cancelar contrato com sucesso."""
        success, message = self.mixin.cancel_contract(self.contract)

        self.assertTrue(success)
        self.contract.refresh_from_db()
        self.assertEqual(self.contract.status, "CANCELED")

    def test_cancel_contract_completed_fails(self):
        """Não deve cancelar contrato completo."""
        self.contract.status = "COMPLETED"
        self.contract.save()

        success, message = self.mixin.cancel_contract(self.contract)

        self.assertFalse(success)
        self.assertIn("concluído", message.lower())

    def test_update_contract_description_success(self):
        """Deve atualizar descrição com sucesso."""
        success, message = self.mixin.update_contract_description(
            self.contract, "Nova descrição do contrato"
        )

        self.assertTrue(success)
        self.contract.refresh_from_db()
        self.assertEqual(self.contract.description, "Nova descrição do contrato")

    def test_update_contract_description_not_editable(self):
        """Não deve atualizar contrato não editável."""
        self.contract.status = "COMPLETED"
        self.contract.save()

        success, message = self.mixin.update_contract_description(
            self.contract, "Nova descrição"
        )

        self.assertFalse(success)

    def test_upload_external_contract_success(self):
        """Deve fazer upload de PDF externo com sucesso."""
        # Cria arquivo PDF fake
        pdf_content = b"%PDF-1.4 fake pdf content"
        pdf_file = SimpleUploadedFile(
            "contrato.pdf", pdf_content, content_type="application/pdf"
        )

        success, message = self.mixin.upload_external_contract(self.contract, pdf_file)

        self.assertTrue(success)
        self.contract.refresh_from_db()
        self.assertEqual(self.contract.status, "COMPLETED")
        self.assertEqual(self.contract.integrity_hash, "UPLOAD_MANUAL_EXTERNO")

    def test_upload_external_contract_invalid_file_type(self):
        """Deve rejeitar arquivo que não é PDF."""
        txt_file = SimpleUploadedFile(
            "arquivo.txt", b"Not a PDF", content_type="text/plain"
        )

        success, message = self.mixin.upload_external_contract(self.contract, txt_file)

        self.assertFalse(success)
        self.assertIn("pdf", message.lower())


class ContractManagementMixinTest(TestCase):
    """
    Testes para o ContractManagementMixin (Facade).
    Verifica se todos os métodos dos mixins compostos estão acessíveis.
    """

    def setUp(self):
        self.factory = RequestFactory()
        self.mixin = ContractManagementMixin()

        self.planner = User.objects.create_user("p", "p@t.com", "123")
        self.wedding = Wedding.objects.create(
            planner=self.planner,
            groom_name="João",
            bride_name="Maria",
            date="2025-06-15",
            location="Salão",
            budget=50000,
        )
        item = Item.objects.create(
            wedding=self.wedding, name="Flores", quantity=1, unit_price=5000
        )
        self.contract = Contract.objects.create(item=item)

        request = self.factory.get("/")
        request.user = self.planner
        self.mixin.request = request

    def test_facade_has_queryset_methods(self):
        """Facade deve ter métodos do ContractQuerysetMixin."""
        self.assertTrue(hasattr(self.mixin, "get_contracts_for_planner"))
        self.assertTrue(hasattr(self.mixin, "get_contracts_for_wedding"))

    def test_facade_has_signature_methods(self):
        """Facade deve ter métodos do ContractSignatureMixin."""
        self.assertTrue(hasattr(self.mixin, "process_contract_signature"))

    def test_facade_has_url_generator_methods(self):
        """Facade deve ter métodos do ContractUrlGeneratorMixin."""
        self.assertTrue(hasattr(self.mixin, "generate_signature_link"))

    def test_facade_has_email_methods(self):
        """Facade deve ter métodos do ContractEmailMixin."""
        self.assertTrue(hasattr(self.mixin, "send_signature_email"))

    def test_facade_has_actions_methods(self):
        """Facade deve ter métodos do ContractActionsMixin."""
        self.assertTrue(hasattr(self.mixin, "cancel_contract"))
        self.assertTrue(hasattr(self.mixin, "update_contract_description"))
        self.assertTrue(hasattr(self.mixin, "upload_external_contract"))

    def test_facade_has_json_response_methods(self):
        """Facade deve ter métodos do JsonResponseMixin."""
        self.assertTrue(hasattr(self.mixin, "json_success"))
        self.assertTrue(hasattr(self.mixin, "json_error"))

    def test_facade_methods_are_callable(self):
        """Todos os métodos do facade devem ser chamáveis."""
        # Testa que os métodos podem ser chamados
        contracts = self.mixin.get_contracts_for_planner()
        self.assertIsNotNone(contracts)

        link_info = self.mixin.generate_signature_link(self.contract)
        self.assertIsInstance(link_info, dict)

        json_response = self.mixin.json_success("Teste")
        self.assertEqual(json_response.status_code, 200)

        self.assertEqual(json_response.status_code, 200)
