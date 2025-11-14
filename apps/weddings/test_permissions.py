from datetime import date

from django.test import TestCase
from django.urls import reverse

from apps.users.models import User
from apps.weddings.models import Wedding


class WeddingOwnerPermissionTestCase(TestCase):
    """Testa as permissões de acesso aos casamentos."""

    def setUp(self):
        """Configuração inicial para os testes."""
        # Cria dois usuários diferentes
        self.owner = User.objects.create_user(
            username="owner", email="owner@example.com", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="other", email="other@example.com", password="testpass123"
        )

        # Cria um casamento pertencente ao owner
        self.wedding = Wedding.objects.create(
            planner=self.owner,
            groom_name="João",
            bride_name="Maria",
            date=date(2025, 12, 31),
            location="São Paulo",
            budget=50000.00,
            status="IN_PROGRESS",
        )

    def test_detail_view_owner_can_access(self):
        """Testa que o owner pode acessar o detalhe do casamento."""
        self.client.login(username="owner", password="testpass123")
        url = reverse("weddings:wedding_detail", kwargs={"wedding_id": self.wedding.pk})
        response = self.client.get(url)

        # O owner deve ter acesso (200 OK)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["wedding"], self.wedding)

    def test_detail_view_other_user_cannot_access(self):
        """Testa que outro usuário não pode acessar o detalhe do casamento."""
        self.client.login(username="other", password="testpass123")
        url = reverse("weddings:wedding_detail", kwargs={"wedding_id": self.wedding.pk})
        response = self.client.get(url)

        # Outro usuário deve ser bloqueado (404 por get_queryset, ou 403/302 por mixin)
        self.assertIn(response.status_code, [403, 404, 302])

    def test_update_view_owner_can_access(self):
        """Testa que o owner pode acessar a página de atualização."""
        self.client.login(username="owner", password="testpass123")
        url = reverse("weddings:edit_wedding", kwargs={"id": self.wedding.pk})
        response = self.client.get(url)

        # O owner deve ter acesso (200 OK)
        self.assertEqual(response.status_code, 200)

    def test_update_view_other_user_cannot_access(self):
        """Testa que outro usuário não pode acessar a página de atualização."""
        self.client.login(username="other", password="testpass123")
        url = reverse("weddings:edit_wedding", kwargs={"id": self.wedding.pk})
        response = self.client.get(url)

        # Outro usuário deve ser bloqueado (404 por get_queryset, ou 403/302 por mixin)
        self.assertIn(response.status_code, [403, 404, 302])

    def test_update_view_owner_can_update(self):
        """Testa que o owner pode atualizar o casamento."""
        self.client.login(username="owner", password="testpass123")
        url = reverse("weddings:edit_wedding", kwargs={"id": self.wedding.pk})

        data = {
            "groom_name": "João Silva",
            "bride_name": "Maria Santos",
            "date": "2025-12-31",
            "location": "Rio de Janeiro",
            "budget": "60000.00",
        }
        response = self.client.post(url, data)

        # O owner deve conseguir atualizar
        # Como usa HTMX, pode retornar 200 ou redirecionar
        self.assertIn(response.status_code, [200, 302])

        # Verifica se foi atualizado
        self.wedding.refresh_from_db()
        self.assertEqual(self.wedding.groom_name, "João Silva")
        self.assertEqual(self.wedding.location, "Rio de Janeiro")

    def test_update_view_other_user_cannot_update(self):
        """Testa que outro usuário não pode atualizar o casamento."""
        self.client.login(username="other", password="testpass123")
        url = reverse("weddings:edit_wedding", kwargs={"id": self.wedding.pk})

        data = {
            "groom_name": "Hacker",
            "bride_name": "Attack",
            "date": "2025-12-31",
            "location": "Nowhere",
            "budget": "1.00",
        }
        response = self.client.post(url, data)

        # Outro usuário deve ser bloqueado (404 por get_queryset, ou 403/302 por mixin)
        self.assertIn(response.status_code, [403, 404, 302])

        # Verifica que não foi atualizado
        self.wedding.refresh_from_db()
        self.assertEqual(self.wedding.groom_name, "João")

    def test_delete_view_owner_can_access(self):
        """Testa que o owner pode acessar a página de exclusão."""
        self.client.login(username="owner", password="testpass123")
        url = reverse("weddings:delete_wedding", kwargs={"id": self.wedding.pk})
        response = self.client.get(url)

        # O owner deve ter acesso (200 OK)
        self.assertEqual(response.status_code, 200)

    def test_delete_view_other_user_cannot_access(self):
        """Testa que outro usuário não pode acessar a página de exclusão."""
        self.client.login(username="other", password="testpass123")
        url = reverse("weddings:delete_wedding", kwargs={"id": self.wedding.pk})
        response = self.client.get(url)

        # Outro usuário deve ser bloqueado (404 por get_queryset, ou 403/302 por mixin)
        self.assertIn(response.status_code, [403, 404, 302])

    def test_delete_view_owner_can_delete(self):
        """Testa que o owner pode excluir o casamento."""
        self.client.login(username="owner", password="testpass123")
        url = reverse("weddings:delete_wedding", kwargs={"id": self.wedding.pk})

        wedding_id = self.wedding.pk
        response = self.client.post(url)

        # O owner deve conseguir excluir
        self.assertIn(response.status_code, [200, 302])

        # Verifica que foi excluído
        self.assertFalse(Wedding.objects.filter(pk=wedding_id).exists())

    def test_delete_view_other_user_cannot_delete(self):
        """Testa que outro usuário não pode excluir o casamento."""
        self.client.login(username="other", password="testpass123")
        url = reverse("weddings:delete_wedding", kwargs={"id": self.wedding.pk})

        response = self.client.post(url)

        # Outro usuário deve ser bloqueado (404 por get_queryset, ou 403/302 por mixin)
        self.assertIn(response.status_code, [403, 404, 302])

        # Verifica que não foi excluído
        self.assertTrue(Wedding.objects.filter(pk=self.wedding.pk).exists())

    def test_update_status_view_owner_can_update(self):
        """Testa que o owner pode atualizar o status do casamento."""
        self.client.login(username="owner", password="testpass123")
        url = reverse("weddings:update_wedding_status", kwargs={"id": self.wedding.pk})

        response = self.client.post(url, {"status": "COMPLETED"})

        # O owner deve conseguir atualizar o status
        self.assertIn(response.status_code, [200, 302])

        # Verifica se o status foi atualizado
        self.wedding.refresh_from_db()
        self.assertEqual(self.wedding.status, "COMPLETED")

    def test_update_status_view_other_user_cannot_update(self):
        """Testa que outro usuário não pode atualizar o status."""
        self.client.login(username="other", password="testpass123")
        url = reverse("weddings:update_wedding_status", kwargs={"id": self.wedding.pk})

        response = self.client.post(url, {"status": "CANCELED"})

        # Outro usuário deve ser bloqueado
        self.assertIn(response.status_code, [400, 403, 302])

        # Verifica que o status não foi alterado
        self.wedding.refresh_from_db()
        self.assertEqual(self.wedding.status, "IN_PROGRESS")

    def test_unauthenticated_user_cannot_access_detail(self):
        """Testa que usuário não autenticado não pode acessar detalhes."""
        url = reverse("weddings:wedding_detail", kwargs={"wedding_id": self.wedding.pk})
        response = self.client.get(url)

        # Deve redirecionar para login
        self.assertEqual(response.status_code, 302)
        self.assertIn("/usuario/login/", response.url)

    def test_unauthenticated_user_cannot_update(self):
        """Testa que usuário não autenticado não pode atualizar."""
        url = reverse("weddings:edit_wedding", kwargs={"id": self.wedding.pk})
        response = self.client.get(url)

        # Deve redirecionar para login
        self.assertEqual(response.status_code, 302)
        self.assertIn("/usuario/login/", response.url)

    def test_unauthenticated_user_cannot_delete(self):
        """Testa que usuário não autenticado não pode excluir."""
        url = reverse("weddings:delete_wedding", kwargs={"id": self.wedding.pk})
        response = self.client.get(url)

        # Deve redirecionar para login
        self.assertEqual(response.status_code, 302)
        self.assertIn("/usuario/login/", response.url)
