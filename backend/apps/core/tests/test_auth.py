from unittest.mock import MagicMock

import pytest

from apps.core.auth import require_user
from apps.core.exceptions import BusinessRuleViolation


@pytest.mark.unit
class TestAuthUtils:
    """Testes para utilitários de autenticação."""

    def test_require_user_with_authenticated_user(self):
        """Garante que retorna o usuário se estiver autenticado."""
        user = MagicMock()
        user.is_authenticated = True

        result = require_user(user)

        assert result == user

    def test_require_user_with_anonymous_user_raises_error(self):
        """Garante que lança erro se o usuário não estiver autenticado."""
        user = MagicMock()
        user.is_authenticated = False

        with pytest.raises(BusinessRuleViolation) as exc:
            require_user(user)

        assert exc.value.code == "authentication_required"
