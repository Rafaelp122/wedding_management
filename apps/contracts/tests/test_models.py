import base64
from datetime import timedelta
from io import BytesIO

from django.test import TestCase
from django.utils import timezone
from PIL import Image

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
            planner=cls.user,
            groom_name="João",
            bride_name="Maria",
            date="2025-06-15",
            location="Salão de Festas",
            budget=50000,
        )
        cls.item = Item.objects.create(
            wedding=cls.wedding,
            name="Fotógrafo",
            quantity=1,
            unit_price=5000,
            supplier="Foto Studio X",
        )

    def test_contract_creation_and_str(self):
        """Verifica criação básica e representação em string."""
        contract = Contract.objects.create(item=self.item, status="WAITING_PLANNER")

        self.assertIn("Fotógrafo", str(contract))
        self.assertEqual(contract.status, "WAITING_PLANNER")

    def test_default_status_is_waiting_planner(self):
        """Status padrão deve ser WAITING_PLANNER."""
        contract = Contract.objects.create(item=self.item)
        self.assertEqual(contract.status, "WAITING_PLANNER")

    def test_property_delegation(self):
        """Verifica se as properties delegam para o Item."""
        contract = Contract.objects.create(item=self.item)

        # Properties devem vir do item
        self.assertEqual(contract.supplier, "Foto Studio X")
        self.assertEqual(contract.wedding, self.wedding)
        self.assertEqual(contract.contract_value, 5000)

    def test_contract_value_calculation(self):
        """Verifica se contract_value calcula corretamente."""
        item = Item.objects.create(
            wedding=self.wedding, name="Buffet", quantity=100, unit_price=50.00
        )
        contract = Contract.objects.create(item=item)

        # 100 * 50 = 5000
        self.assertEqual(contract.contract_value, 5000)

    def test_item_deletion_cascades_to_contract(self):
        """Se o Item for deletado, o Contrato também deve ser."""
        contract = Contract.objects.create(item=self.item)
        contract_pk = contract.pk

        self.item.delete()

        self.assertFalse(Contract.objects.filter(pk=contract_pk).exists())

    def test_one_to_one_constraint(self):
        """Não pode criar dois contratos para o mesmo item."""
        from django.db.utils import IntegrityError

        Contract.objects.create(item=self.item)

        with self.assertRaises(IntegrityError):
            Contract.objects.create(item=self.item)


class ContractSignatureProcessingTest(TestCase):
    """Testes para o método process_signature do modelo Contract."""

    def setUp(self):
        self.user = User.objects.create_user("planner", "p@test.com", "123")
        self.wedding = Wedding.objects.create(
            planner=self.user,
            groom_name="João",
            bride_name="Maria",
            date="2025-06-15",
            location="Salão",
            budget=50000,
        )
        self.item = Item.objects.create(
            wedding=self.wedding,
            name="Decoração",
            quantity=1,
            unit_price=3000,
            supplier="Flores & Cia",
        )
        self.contract = Contract.objects.create(
            item=self.item, status="WAITING_PLANNER"
        )

    def _create_fake_signature_base64(self, format="png"):
        """Helper para criar uma imagem base64 fake."""
        img = Image.new("RGB", (100, 50), color="white")
        buffer = BytesIO()
        img.save(buffer, format=format.upper())
        img_bytes = buffer.getvalue()
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")
        return f"data:image/{format};base64,{img_b64}"

    def test_process_signature_empty_raises_error(self):
        """Assinatura vazia deve lançar ValueError."""
        with self.assertRaises(ValueError) as cm:
            self.contract.process_signature("", "192.168.1.1")

        self.assertIn("inválida ou vazia", str(cm.exception))

    def test_process_signature_invalid_format_raises_error(self):
        """Formato sem base64 deve lançar ValueError."""
        with self.assertRaises(ValueError) as cm:
            self.contract.process_signature(
                "invalid_data_without_base64", "192.168.1.1"
            )

        self.assertIn("inválida ou vazia", str(cm.exception))

    def test_process_signature_unsupported_format_raises_error(self):
        """Formato não permitido (ex: gif) deve lançar ValueError."""
        # Cria base64 de um formato não permitido
        fake_sig = (
            "data:image/gif;base64,"
            "R0lGODlhAQABAIAAAP///wAAACH5BAAAAAAALAAAAAABAAEAAAICRAEAOw=="
        )

        with self.assertRaises(ValueError) as cm:
            self.contract.process_signature(fake_sig, "192.168.1.1")

        self.assertIn("não permitido", str(cm.exception))

    def test_process_signature_too_large_raises_error(self):
        """Assinatura maior que 500KB deve lançar ValueError."""
        # Cria imagem grande no formato JPEG sem compressão
        # 3000x3000 pixels em RGB resulta em ~2MB sem compressão
        width, height = 3000, 3000

        # Cria imagem com gradiente para evitar compressão eficiente
        large_img = Image.new("RGB", (width, height))
        pixels = large_img.load()
        self.assertIsNotNone(pixels, "Failed to load image pixels")

        # Preenche com padrão complexo que não comprime bem
        for i in range(width):
            for j in range(height):
                # Cria padrão único para cada pixel
                r = (i * j) % 256
                g = (i + j) % 256
                b = (i - j) % 256
                pixels[i, j] = (r, g, b)  # type: ignore[index]

        buffer = BytesIO()
        # Salva como JPEG com qualidade máxima (sem compressão)
        large_img.save(buffer, format="JPEG", quality=100)
        img_bytes = buffer.getvalue()

        # Verifica que é realmente > 500KB
        size_kb = len(img_bytes) / 1024
        self.assertGreater(
            len(img_bytes), 500 * 1024, f"Imagem tem apenas {size_kb:.1f}KB"
        )

        img_b64 = base64.b64encode(img_bytes).decode("utf-8")
        fake_sig = f"data:image/jpeg;base64,{img_b64}"

        with self.assertRaises(ValueError) as cm:
            self.contract.process_signature(fake_sig, "192.168.1.1")

        # Verifica mensagem de erro
        self.assertIn("muito grande", str(cm.exception))

        self.assertIn("muito grande", str(cm.exception))

    def test_process_signature_planner_success(self):
        """Processar assinatura do planner com sucesso."""
        sig = self._create_fake_signature_base64()

        self.contract.process_signature(sig, "192.168.1.1")
        self.contract.refresh_from_db()

        # Verifica mudanças
        self.assertEqual(self.contract.status, "WAITING_SUPPLIER")
        self.assertIsNotNone(self.contract.planner_signature)
        self.assertIsNotNone(self.contract.planner_signed_at)
        self.assertEqual(self.contract.planner_ip, "192.168.1.1")

    def test_process_signature_supplier_success(self):
        """Processar assinatura do fornecedor com sucesso."""
        sig = self._create_fake_signature_base64()

        # Primeiro assina como planner
        self.contract.status = "WAITING_SUPPLIER"
        self.contract.save()

        self.contract.process_signature(sig, "10.0.0.1")
        self.contract.refresh_from_db()

        self.assertEqual(self.contract.status, "WAITING_COUPLE")
        self.assertIsNotNone(self.contract.supplier_signature)
        self.assertIsNotNone(self.contract.supplier_signed_at)
        self.assertEqual(self.contract.supplier_ip, "10.0.0.1")

    def test_process_signature_couple_success_generates_hash(self):
        """Assinatura dos noivos gera hash de integridade."""
        sig = self._create_fake_signature_base64()

        # Simula que já foi assinado por planner e supplier
        self.contract.status = "WAITING_COUPLE"
        self.contract.planner_signed_at = timezone.now()
        self.contract.planner_ip = "192.168.1.1"
        self.contract.supplier_signed_at = timezone.now()
        self.contract.supplier_ip = "10.0.0.1"
        self.contract.save()

        self.contract.process_signature(sig, "172.16.0.1")
        self.contract.refresh_from_db()

        # Verifica status final
        self.assertEqual(self.contract.status, "COMPLETED")
        self.assertIsNotNone(self.contract.couple_signature)
        self.assertIsNotNone(self.contract.couple_signed_at)
        self.assertEqual(self.contract.couple_ip, "172.16.0.1")

        # Verifica se o hash foi gerado
        self.assertIsNotNone(self.contract.integrity_hash)
        self.assertEqual(len(self.contract.integrity_hash), 64)  # SHA256

    def test_process_signature_wrong_status_raises_error(self):
        """Assinar em status inválido deve lançar RuntimeError."""
        sig = self._create_fake_signature_base64()

        self.contract.status = "COMPLETED"
        self.contract.save()

        with self.assertRaises(RuntimeError) as cm:
            self.contract.process_signature(sig, "192.168.1.1")

        self.assertIn("Não é possível assinar", str(cm.exception))


class ContractNextSignerInfoTest(TestCase):
    """Testes para o método get_next_signer_info."""

    def setUp(self):
        self.user = User.objects.create_user("planner", "p@test.com", "123")
        self.wedding = Wedding.objects.create(
            planner=self.user,
            groom_name="Carlos",
            bride_name="Ana",
            date="2025-06-15",
            location="Igreja",
            budget=30000,
        )
        self.item = Item.objects.create(
            wedding=self.wedding,
            name="DJ",
            quantity=1,
            unit_price=2000,
            supplier="Som & Luz",
        )
        self.contract = Contract.objects.create(item=self.item)

    def test_next_signer_waiting_planner(self):
        """Status WAITING_PLANNER retorna info do cerimonialista."""
        info = self.contract.get_next_signer_info()

        self.assertEqual(info["role"], "Cerimonialista")
        self.assertIn("Cerimonialista", info["name"])

    def test_next_signer_waiting_supplier(self):
        """Status WAITING_SUPPLIER retorna info do fornecedor."""
        self.contract.status = "WAITING_SUPPLIER"
        self.contract.save()

        info = self.contract.get_next_signer_info()

        self.assertEqual(info["role"], "Fornecedor")
        self.assertIn("Som & Luz", info["name"])

    def test_next_signer_waiting_supplier_no_supplier_name(self):
        """Fornecedor sem nome retorna 'Não vinculado'."""
        self.item.supplier = ""
        self.item.save()

        self.contract.status = "WAITING_SUPPLIER"
        self.contract.save()

        info = self.contract.get_next_signer_info()

        self.assertIn("Não vinculado", info["name"])

    def test_next_signer_waiting_couple(self):
        """Status WAITING_COUPLE retorna info dos noivos."""
        self.contract.status = "WAITING_COUPLE"
        self.contract.save()

        info = self.contract.get_next_signer_info()

        self.assertEqual(info["role"], "Noivos")
        self.assertIn("Carlos", info["name"])
        self.assertIn("Ana", info["name"])

    def test_next_signer_completed(self):
        """Status COMPLETED retorna info genérica."""
        self.contract.status = "COMPLETED"
        self.contract.save()

        info = self.contract.get_next_signer_info()

        self.assertEqual(info["role"], "Desconhecido")


class ContractIntegrityHashTest(TestCase):
    """Testes para geração de hash de integridade."""

    def setUp(self):
        self.user = User.objects.create_user("planner", "p@test.com", "123")
        self.wedding = Wedding.objects.create(
            planner=self.user,
            groom_name="Pedro",
            bride_name="Julia",
            date="2025-12-20",
            location="Praia",
            budget=80000,
        )
        self.item = Item.objects.create(
            wedding=self.wedding, name="Buffet", quantity=150, unit_price=80
        )
        self.contract = Contract.objects.create(item=self.item)

    def test_integrity_hash_includes_all_signatures(self):
        """Hash deve incluir dados de todas as assinaturas."""
        # Simula todas as assinaturas
        now = timezone.now()
        self.contract.planner_signed_at = now
        self.contract.planner_ip = "192.168.1.1"
        self.contract.supplier_signed_at = now
        self.contract.supplier_ip = "10.0.0.1"
        self.contract.couple_signed_at = now
        self.contract.couple_ip = "172.16.0.1"

        # Chama o método interno
        self.contract._generate_integrity_hash()

        # Verifica se o hash foi gerado
        self.assertIsNotNone(self.contract.integrity_hash)
        self.assertEqual(len(self.contract.integrity_hash), 64)

    def test_integrity_hash_is_deterministic(self):
        """Mesmos dados devem gerar mesmo hash."""
        now = timezone.now()
        self.contract.planner_signed_at = now
        self.contract.planner_ip = "192.168.1.1"
        self.contract.supplier_signed_at = now
        self.contract.supplier_ip = "10.0.0.1"
        self.contract.couple_signed_at = now
        self.contract.couple_ip = "172.16.0.1"

        self.contract._generate_integrity_hash()
        hash1 = self.contract.integrity_hash

        self.contract._generate_integrity_hash()
        hash2 = self.contract.integrity_hash

        self.assertEqual(hash1, hash2)


class ContractStatusMethodsTest(TestCase):
    """Testes para métodos de verificação de status
    (is_fully_signed, get_signatures_status)."""

    def setUp(self):
        planner = User.objects.create_user("p", "p@t.com", "123")
        wedding = Wedding.objects.create(
            planner=planner,
            groom_name="João",
            bride_name="Maria",
            date=timezone.now().date() + timedelta(days=90),
            location="Igreja",
            budget=80000,
        )
        item = Item.objects.create(
            wedding=wedding,
            name="Flores",
            quantity=1,
            unit_price=5000,
            supplier="Flora Bella",
        )
        self.contract = Contract.objects.create(item=item, status="WAITING_PLANNER")

    def _create_fake_signature(self):
        """Helper para criar assinatura fake."""
        img = Image.new("RGB", (100, 50), color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_bytes = buffer.getvalue()
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")
        return f"data:image/png;base64,{img_b64}"

    def test_is_fully_signed_returns_false_initially(self):
        """Contrato inicial não está totalmente assinado."""
        self.assertFalse(self.contract.is_fully_signed())

    def test_is_fully_signed_returns_true_when_complete(self):
        """Contrato com todas as assinaturas retorna True."""
        sig = self._create_fake_signature()

        # Simula processo completo de assinatura
        self.contract.process_signature(sig, "1.1.1.1")
        self.contract.process_signature(sig, "2.2.2.2")
        self.contract.process_signature(sig, "3.3.3.3")

        self.assertTrue(self.contract.is_fully_signed())
        self.assertEqual(self.contract.status, "COMPLETED")

    def test_get_signatures_status_returns_dict(self):
        """get_signatures_status deve retornar dict com 3 chaves."""
        status = self.contract.get_signatures_status()

        self.assertIsInstance(status, dict)
        self.assertIn("planner", status)
        self.assertIn("supplier", status)
        self.assertIn("couple", status)

    def test_signatures_status_structure(self):
        """Cada entrada deve ter signed, signed_at, ip."""
        status = self.contract.get_signatures_status()

        for party in ["planner", "supplier", "couple"]:
            self.assertIn("signed", status[party])
            self.assertIn("signed_at", status[party])
            self.assertIn("ip", status[party])

    def test_signatures_status_updates_after_signing(self):
        """Status deve atualizar após assinatura."""
        sig = self._create_fake_signature()

        # Antes
        status_before = self.contract.get_signatures_status()
        self.assertFalse(status_before["planner"]["signed"])

        # Assina
        self.contract.process_signature(sig, "192.168.1.1")

        # Depois
        status_after = self.contract.get_signatures_status()
        self.assertTrue(status_after["planner"]["signed"])
        self.assertEqual(status_after["planner"]["ip"], "192.168.1.1")
        self.assertIsNotNone(status_after["planner"]["signed_at"])
