"""
Testes dos serializers da API de Users.
"""
from django.test import TestCase

from apps.users.models import User
from apps.users.api.serializers import (
    ChangePasswordSerializer,
    UserDetailSerializer,
    UserListSerializer,
    UserSerializer,
)


class UserSerializerTest(TestCase):
    """Testes do UserSerializer (CRUD)."""

    def test_serialization(self):
        """Testa a serialização de um usuário."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User"
        )

        serializer = UserSerializer(user)
        data = serializer.data

        self.assertEqual(data["id"], user.id)
        self.assertEqual(data["username"], "testuser")
        self.assertEqual(data["email"], "test@example.com")
        self.assertEqual(data["first_name"], "Test")
        self.assertEqual(data["last_name"], "User")
        self.assertNotIn("password", data)  # Write-only
        self.assertIn("date_joined", data)

    def test_deserialization_valid(self):
        """Testa a desserialização com dados válidos."""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "newpass123",
            "password2": "newpass123",
        }

        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        user = serializer.save()
        self.assertEqual(user.username, "newuser")
        self.assertEqual(user.email, "newuser@example.com")
        self.assertTrue(user.check_password("newpass123"))
        self.assertTrue(user.is_active)

    def test_validation_password_mismatch(self):
        """Testa validação quando senhas não coincidem."""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "pass123",
            "password2": "different",
        }

        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password2", serializer.errors)

    def test_update_without_password(self):
        """Testa atualização sem alterar senha."""
        user = User.objects.create_user(
            username="olduser",
            email="old@example.com",
            password="oldpass123"
        )
        old_password = user.password

        data = {
            "first_name": "Updated",
            "last_name": "Name",
        }

        serializer = UserSerializer(user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()

        self.assertEqual(updated_user.first_name, "Updated")
        self.assertEqual(updated_user.password, old_password)  # Inalterado


class UserListSerializerTest(TestCase):
    """Testes do UserListSerializer (otimizado para listagem)."""

    def test_serialization_with_full_name(self):
        """Testa serialização com nome completo."""
        user = User.objects.create_user(
            username="listuser",
            email="list@example.com",
            password="pass123",
            first_name="John",
            last_name="Doe"
        )

        serializer = UserListSerializer(user)
        data = serializer.data

        self.assertEqual(data["id"], user.id)
        self.assertEqual(data["username"], "listuser")
        self.assertEqual(data["full_name"], "John Doe")

    def test_full_name_fallback_to_username(self):
        """Testa que full_name usa username se nome não fornecido."""
        user = User.objects.create_user(
            username="noname",
            email="noname@example.com",
            password="pass123"
        )

        serializer = UserListSerializer(user)
        self.assertEqual(serializer.data["full_name"], "noname")


class UserDetailSerializerTest(TestCase):
    """Testes do UserDetailSerializer (detalhes completos)."""

    def test_serialization_with_counts(self):
        """Testa serialização com contagens de recursos."""
        from decimal import Decimal
        from apps.weddings.models import Wedding
        from apps.scheduler.models import Event

        user = User.objects.create_user(
            username="planner",
            email="planner@example.com",
            password="pass123",
            first_name="Jane",
            last_name="Planner"
        )

        # Cria 2 casamentos
        Wedding.objects.create(
            planner=user,
            groom_name="Groom1",
            bride_name="Bride1",
            date="2025-12-31",
            location="Location",
            budget=Decimal("10000.00")
        )
        Wedding.objects.create(
            planner=user,
            groom_name="Groom2",
            bride_name="Bride2",
            date="2025-11-30",
            location="Location",
            budget=Decimal("15000.00")
        )

        # Cria 3 eventos
        from django.utils import timezone
        for i in range(3):
            Event.objects.create(
                planner=user,
                title=f"Event {i}",
                start_time=timezone.now(),
                event_type="reuniao"
            )

        serializer = UserDetailSerializer(user)
        data = serializer.data

        self.assertEqual(data["id"], user.id)
        self.assertEqual(data["full_name"], "Jane Planner")
        self.assertEqual(data["weddings_count"], 2)
        self.assertEqual(data["events_count"], 3)


class ChangePasswordSerializerTest(TestCase):
    """Testes do ChangePasswordSerializer."""

    def test_validation_password_mismatch(self):
        """Testa validação quando novas senhas não coincidem."""
        data = {
            "old_password": "oldpass123",
            "new_password": "newpass123",
            "new_password2": "different",
        }

        serializer = ChangePasswordSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("new_password2", serializer.errors)

    def test_valid_data(self):
        """Testa que dados válidos passam na validação."""
        data = {
            "old_password": "oldpass123",
            "new_password": "newpass123",
            "new_password2": "newpass123",
        }

        serializer = ChangePasswordSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
