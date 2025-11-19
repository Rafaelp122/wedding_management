from django.test import TestCase
from django.core.exceptions import ValidationError
from apps.pages.models import ContactInquiry


class ContactInquiryModelTest(TestCase):
    def test_create_valid_inquiry(self):
        """
        Deve criar uma mensagem de contato com sucesso e verificar defaults.
        """
        inquiry = ContactInquiry.objects.create(
            name="Visitante",
            email="visita@teste.com",
            message="Gostaria de saber mais."
        )

        # Verifica persistência
        self.assertEqual(inquiry.name, "Visitante")
        self.assertEqual(inquiry.email, "visita@teste.com")

        # Verifica default de 'read'
        self.assertFalse(inquiry.read)

        # Verifica __str__
        self.assertEqual(str(inquiry), "Mensagem de Visitante (visita@teste.com)")

    def test_ordering_latest_first(self):
        """
        A ordenação deve ser decrescente por created_at (mais novos primeiro).
        """
        # Criamos o antigo
        msg_old = ContactInquiry.objects.create(
            name="Old", email="old@t.com", message="msg"
        )

        # Criamos o novo
        msg_new = ContactInquiry.objects.create(
            name="New", email="new@t.com", message="msg"
        )

        # Forçamos datas diferentes caso o teste rode rápido demais (no mesmo milissegundo)
        # O BaseModel usa auto_now_add, então precisamos atualizar manualmente via SQL ou mock.
        # Uma forma simples é usar update() que vai direto no banco
        from django.utils import timezone
        from datetime import timedelta

        ContactInquiry.objects.filter(pk=msg_old.pk).update(
            created_at=timezone.now() - timedelta(hours=1)
        )

        # Busca todos
        inquiries = list(ContactInquiry.objects.all())

        # O primeiro da lista deve ser o msg_new
        self.assertEqual(inquiries[0], msg_new)
        self.assertEqual(inquiries[1], msg_old)

    def test_name_max_length_validation(self):
        """
        Deve falhar se o nome tiver mais que 100 caracteres.
        """
        long_name = "a" * 101
        inquiry = ContactInquiry(
            name=long_name,
            email="valid@test.com",
            message="msg"
        )

        with self.assertRaises(ValidationError):
            inquiry.full_clean()

    def test_mark_as_read_method(self):
        """
        Testa o método helper mark_as_read (se você optou por implementá-lo).
        """
        inquiry = ContactInquiry.objects.create(
            name="Tester", email="t@t.com", message="msg"
        )

        self.assertFalse(inquiry.read)

        inquiry.mark_as_read()

        # Deve ter atualizado no objeto e no banco
        self.assertTrue(inquiry.read)

        inquiry.refresh_from_db()
        self.assertTrue(inquiry.read)

    def test_invalid_email_format(self):
        """
        Deve lançar ValidationError se o email não for válido (ex: sem @).
        """
        inquiry = ContactInquiry(
            name="Hacker",
            email="email-invalido",  # Sem @ ou domínio
            message="spam"
        )

        with self.assertRaises(ValidationError):
            inquiry.full_clean()
