"""Testes do modelo User."""

from typing import Any, cast

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db import models as db_models

from apps.users.models import User as UserModel

from .factories import AdminFactory as _AdminFactory
from .factories import UserFactory as _UserFactory


User = get_user_model()


def UserFactory(*args: Any, **kwargs: Any) -> UserModel:
    return cast(UserModel, _UserFactory(*args, **kwargs))


def AdminFactory(*args: Any, **kwargs: Any) -> UserModel:
    return cast(UserModel, _AdminFactory(*args, **kwargs))


@pytest.mark.django_db
class TestUserModel:
    """Testes do modelo customizado User com campos explícitos e Factories."""

    def test_create_user_via_manager(self) -> None:
        """Testa se o Manager cria o usuário com os campos separados corretamente."""
        user = User.objects.create_user(
            email="manager_test@example.com",
            first_name="Nome",
            last_name="Sobrenome",
            password="password123",
        )
        assert user.email == "manager_test@example.com"
        assert user.first_name == "Nome"
        assert user.last_name == "Sobrenome"
        assert user.check_password("password123")
        assert not user.is_active  # Valida regra de negócio: inativo por padrão

    def test_create_superuser_via_manager(self) -> None:
        """Testa se o Manager cria o superusuário com as permissões corretas."""
        admin = User.objects.create_superuser(
            email="admin_manager@example.com",
            first_name="Admin",
            last_name="Root",
            password="adminpassword",
        )
        assert admin.is_staff
        assert admin.is_superuser
        assert admin.is_active

    def test_user_factory_creation(self) -> None:
        """Valida que a UserFactory gera usuários ativos e válidos para testes."""
        user = UserFactory()
        assert user.is_active is True
        assert "@" in user.email
        assert len(user.first_name) > 0

    def test_admin_factory_creation(self) -> None:
        """Valida que a AdminFactory gera superusuários corretamente."""
        admin = AdminFactory()
        assert admin.is_superuser is True
        assert admin.is_staff is True

    def test_user_email_required(self) -> None:
        """Testa a obrigatoriedade do email no nível do Manager."""
        with pytest.raises(ValueError, match="O e-mail é obrigatório"):
            User.objects.create_user(email="", first_name="User", last_name="Test")

    def test_user_email_unique(self) -> None:
        """Testa a restrição de unicidade do email no banco de dados."""
        UserFactory(email="unique@example.com")
        with pytest.raises(IntegrityError):
            # Tentativa de criar outro usuário com o mesmo email via Factory
            UserFactory(email="unique@example.com")

    def test_user_str_representation(self) -> None:
        """Testa o dunder method __str__ usando dados da Factory."""
        user = UserFactory(first_name="Dunder", last_name="Method", email="test@ex.com")
        assert str(user) == "Dunder Method (test@ex.com)"

    def test_get_full_name(self) -> None:
        """Testa se a união do nome e sobrenome está correta."""
        user = UserFactory(first_name="Full", last_name="Name")
        assert user.get_full_name() == "Full Name"

    def test_get_short_name(self) -> None:
        """Testa se o nome curto retorna apenas o first_name."""
        user = UserFactory(first_name="Short", last_name="LongName")
        assert user.get_short_name() == "Short"

    def test_email_normalization(self) -> None:
        """Testa se o Manager normaliza o domínio do email para minúsculo."""
        email_mixed = "USER@DOMAIN.COM"
        user = User.objects.create_user(
            email=email_mixed,
            first_name="Test",
            last_name="Normalization",
            password="pass",
        )
        assert user.email == "USER@domain.com"


@pytest.mark.django_db
class TestUserCompanyProtect:
    """Testes da constraint on_delete=PROTECT no FK company."""

    def test_delete_company_with_users_raises_protected_error(self) -> None:
        """Não é possível deletar Company que possui Users vinculados."""
        user = UserFactory()
        company = user.company

        with pytest.raises(db_models.ProtectedError):
            company.delete()
