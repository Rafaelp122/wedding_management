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
            email="test@example.com", password="testpass123"
        )
        assert user.username == "test"  # Auto-generated from email
        assert user.email == "test@example.com"
        assert user.check_password("testpass123")
        assert not user.is_staff
        assert not user.is_superuser
        assert user.is_active

    def test_create_superuser(self):
        """Testa criação de superusuário."""
        admin = User.objects.create_superuser(
            email="admin@example.com", password="adminpass123"
        )
        assert admin.is_staff
        assert admin.is_superuser
        assert admin.is_active

    def test_user_email_required(self):
        """Testa que email é obrigatório."""
        with pytest.raises(ValueError, match="O campo de E-mail é obrigatório"):
            User.objects.create_user(email="", password="testpass123")

    def test_user_username_auto_generated(self):
        """Testa que username é gerado automaticamente a partir do email."""
        user = User.objects.create_user(
            email="john.doe@example.com", password="testpass123"
        )
        assert user.username == "john.doe"  # Part before @

    def test_user_email_unique(self):
        """Testa que email deve ser único."""
        User.objects.create_user(email="same@example.com", password="pass123")
        with pytest.raises(IntegrityError):
            User.objects.create_user(email="same@example.com", password="pass123")

    def test_user_username_unique(self):
        """Testa que username deve ser único."""
        User.objects.create_user(
            email="email1@example.com", username="sameuser", password="pass123"
        )
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                email="email2@example.com", username="sameuser", password="pass123"
            )

    def test_user_str_representation(self):
        """Testa representação string do usuário."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        assert str(user) == user.email
