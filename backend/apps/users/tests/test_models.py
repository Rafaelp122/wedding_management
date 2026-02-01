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
            username="testuser", email="test@example.com", password="testpass123"
        )
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.check_password("testpass123")
        assert not user.is_staff
        assert not user.is_superuser
        assert user.is_active

    def test_create_superuser(self):
        """Testa criação de superusuário."""
        admin = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass123"
        )
        assert admin.is_staff
        assert admin.is_superuser
        assert admin.is_active

    def test_user_email_required(self):
        """Testa que email é obrigatório."""
        with pytest.raises(ValueError, match="O campo de E-mail é obrigatório"):
            User.objects.create_user(
                username="testuser", email="", password="testpass123"
            )

    def test_user_username_required(self):
        """Testa que username é obrigatório."""
        with pytest.raises(ValueError, match="O campo de Username é obrigatório"):
            User.objects.create_user(
                username="", email="test@example.com", password="testpass123"
            )

    def test_user_email_unique(self):
        """Testa que email deve ser único."""
        User.objects.create_user(
            username="user1", email="same@example.com", password="pass123"
        )
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                username="user2", email="same@example.com", password="pass123"
            )

    def test_user_username_unique(self):
        """Testa que username deve ser único."""
        User.objects.create_user(
            username="sameuser", email="email1@example.com", password="pass123"
        )
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                username="sameuser", email="email2@example.com", password="pass123"
            )

    def test_user_str_representation(self):
        """Testa representação string do usuário."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        # Se não há __str__ customizado, usa o padrão do AbstractUser
        assert str(user) == "testuser"
