import pytest
from django.contrib.auth.models import AnonymousUser

from apps.core.exceptions import BusinessRuleViolation
from apps.users.auth import require_user
from apps.users.tests.factories import UserFactory


pytestmark = pytest.mark.django_db


class TestRequireUser:
    """Testes para require_user()."""

    def test_require_user_authenticated_returns_user(self):
        """Usuário autenticado deve retornar a instância de User."""
        user = UserFactory(is_active=True)

        result = require_user(user)

        assert result == user
        assert result.is_authenticated

    def test_require_user_unauthenticated_raises_error(self):
        """Usuário não autenticado deve levantar BusinessRuleViolation."""
        anon = AnonymousUser()

        with pytest.raises(BusinessRuleViolation) as exc_info:
            require_user(anon)

        assert exc_info.value.code == "authentication_required"
