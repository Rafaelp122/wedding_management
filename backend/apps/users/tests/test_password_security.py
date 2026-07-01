import pytest
from django.core.exceptions import ValidationError

from apps.users.services.registration_service import RegistrationService


@pytest.mark.django_db
class TestRegistrationPasswordSecurity:
    """Testes de segurança para validação de senha no registro."""

    def test_register_new_owner_with_weak_password_fails(self):
        """
        Garante que senhas fracas (comuns) são rejeitadas durante o registro.
        """
        email = "weak-password@example.com"
        # 'password' deve ser bloqueada pelo CommonPasswordValidator
        weak_password = "password"

        # Este teste deve levantar ValidationError após a correção
        with pytest.raises(ValidationError):
            RegistrationService.register_new_owner(
                email=email,
                password=weak_password,
                first_name="Weak",
                last_name="Password"
            )
