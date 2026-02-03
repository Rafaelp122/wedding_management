"""Testes do modelo User."""

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Testes do modelo customizado User."""

    def test_create_user(self):
        """Testa criação de usuário comum."""
        user = User.objects.create_user(
            email="test@example.com", name="Test User", password="testpass123"
        )
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.check_password("testpass123")
        assert not user.is_staff
        assert not user.is_superuser
        assert not user.is_active  # Usuários comuns começam inativos

    def test_create_superuser(self):
        """Testa criação de superusuário."""
        admin = User.objects.create_superuser(
            email="admin@example.com", name="Admin User", password="adminpass123"
        )
        assert admin.email == "admin@example.com"
        assert admin.name == "Admin User"
        assert admin.is_staff
        assert admin.is_superuser
        assert admin.is_active

    def test_user_email_required(self):
        """Testa que email é obrigatório."""
        with pytest.raises(ValueError, match="O e-mail é obrigatório"):
            User.objects.create_user(email="", name="Test User", password="testpass123")

    def test_user_email_unique(self):
        """Testa que email deve ser único."""
        User.objects.create_user(
            email="same@example.com", name="User One", password="pass123"
        )
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                email="same@example.com", name="User Two", password="pass123"
            )

    def test_user_str_representation(self):
        """Testa representação string do usuário."""
        user = User.objects.create_user(
            email="test@example.com", name="João Silva", password="pass123"
        )
        assert str(user) == "João Silva (test@example.com)"

    def test_get_full_name(self):
        """Testa método get_full_name."""
        user = User.objects.create_user(
            email="test@example.com", name="João Silva", password="pass123"
        )
        assert user.get_full_name() == "João Silva"

    def test_get_short_name(self):
        """Testa método get_short_name."""
        user = User.objects.create_user(
            email="test@example.com", name="João Silva Santos", password="pass123"
        )
        assert user.get_short_name() == "João"

    def test_get_short_name_fallback_to_email(self):
        """Testa que get_short_name retorna email se nome estiver vazio."""
        user = User.objects.create_user(
            email="test@example.com", name="", password="pass123"
        )
        assert user.get_short_name() == "test@example.com"

    def test_email_normalization(self):
        """Testa que email é normalizado (lowercase no domínio)."""
        user = User.objects.create_user(
            email="Test@EXAMPLE.COM", name="Test User", password="pass123"
        )
        assert user.email == "Test@example.com"  # Domínio normalizado
