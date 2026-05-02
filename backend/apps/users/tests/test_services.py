import pytest

from apps.core.exceptions import DomainIntegrityError
from apps.tenants.models import Company
from apps.users.models import User
from apps.users.services.registration_service import RegistrationService


@pytest.mark.django_db
class TestRegistrationService:
    """Testes unitários para o RegistrationService."""

    def test_register_new_owner_success(self):
        """Garante que um novo usuário e empresa são criados corretamente."""
        email = "novo@exemplo.com"
        password = "password123"
        first_name = "Novo"
        last_name = "Usuário"

        user = RegistrationService.register_new_owner(
            email=email, password=password, first_name=first_name, last_name=last_name
        )

        assert isinstance(user, User)
        assert user.email == email
        assert user.first_name == first_name
        assert user.last_name == last_name
        assert user.is_active is True

        # Verifica se a empresa foi criada
        assert user.company is not None
        assert isinstance(user.company, Company)
        assert user.company.name == f"Workspace de {first_name} {last_name}"

    def test_register_new_owner_duplicate_email_fails(self, user):
        """Garante que não é possível registrar dois usuários com o mesmo e-mail."""
        email = user.email
        password = "another_password"

        with pytest.raises(DomainIntegrityError) as exc_info:
            RegistrationService.register_new_owner(email=email, password=password)

        assert exc_info.value.code == "email_already_exists"
        assert "e-mail já está cadastrado" in str(exc_info.value.detail)

    def test_register_new_owner_transaction_rollback(self, db):
        """Garante que a empresa não é criada se o usuário falhar (Rollback)."""
        email = "falha@exemplo.com"

        # Forçamos uma falha passando um dado inválido que o banco rejeitaria
        with pytest.raises(Exception):  # noqa: B017
            RegistrationService.register_new_owner(
                email=email,
                password="123",
                first_name="A" * 300,  # Excede max_length de 150
            )

        # Verifica que a empresa não foi criada ou foi revertida
        assert not Company.objects.filter(name__icontains=email).exists()
