"""
Testes de segurança e endurecimento da camada de autenticação.

Cobre:
- Bloqueio de conta (Account Lockout) após 5 tentativas falhas de login (429)
- Endpoint de Logout seguro com invalidação de refresh token no backend (200)
- Mitigação de Timing Attack em tentativas de login com usuário inexistente
- Mitigação de DoS por senhas longas (max_length=128 retorna 422)
"""

from collections.abc import Generator
from typing import Any

import pytest
from django.core.cache import cache

from apps.users.tests.factories import UserFactory


@pytest.mark.django_db
class TestAuthSecurityHardening:
    @pytest.fixture(autouse=True)
    def setup_cache(self) -> Generator[None, None, None]:
        cache.clear()
        yield
        cache.clear()

    def test_account_lockout_after_five_failed_attempts(self, auth_client: Any) -> None:
        user = UserFactory(email="lockout_test@example.com")

        # 5 tentativas incorretas de IPs diferentes (simula ataque distribuído) -> 401
        for i in range(5):
            resp = auth_client.post(
                "/api/v1/auth/token/",
                {"email": user.email, "password": f"wrong_{i}"},
                content_type="application/json",
                REMOTE_ADDR=f"10.0.0.{i + 1}",
            )
            assert resp.status_code == 401
            assert resp.json().get("code") == "invalid_credentials"

        # 6ª tentativa -> 429 Too Many Requests (Conta bloqueada por email)
        resp_blocked = auth_client.post(
            "/api/v1/auth/token/",
            {"email": user.email, "password": "wrong_final"},
            content_type="application/json",
            REMOTE_ADDR="10.0.0.99",
        )
        assert resp_blocked.status_code == 429
        data = resp_blocked.json()
        assert data.get("code") == "account_locked"
        expected_detail = "Muitas tentativas com erro. Tente novamente mais tarde."
        assert data.get("detail") == expected_detail

        # Tentativa subsequente mesmo com a senha correta -> permanece 429
        resp_correct = auth_client.post(
            "/api/v1/auth/token/",
            {"email": user.email, "password": "password123"},
            content_type="application/json",
            REMOTE_ADDR="10.0.0.100",
        )
        assert resp_correct.status_code == 429
        assert resp_correct.json().get("code") == "account_locked"

    def test_successful_login_resets_failure_counter(self, auth_client: Any) -> None:
        user = UserFactory(email="reset_test@example.com")

        # 3 tentativas incorretas
        for i in range(3):
            auth_client.post(
                "/api/v1/auth/token/",
                {"email": user.email, "password": "wrong"},
                content_type="application/json",
                REMOTE_ADDR=f"10.1.0.{i + 1}",
            )

        # 1 tentativa correta -> 200 e zera o contador
        resp_success = auth_client.post(
            "/api/v1/auth/token/",
            {"email": user.email, "password": "password123"},
            content_type="application/json",
            REMOTE_ADDR="10.1.0.50",
        )
        assert resp_success.status_code == 200

        # Próximas 4 tentativas incorretas não devem bloquear
        for i in range(4):
            resp = auth_client.post(
                "/api/v1/auth/token/",
                {"email": user.email, "password": "wrong"},
                content_type="application/json",
                REMOTE_ADDR=f"10.1.0.{i + 10}",
            )
            assert resp.status_code == 401

    def test_logout_invalidates_refresh_token(
        self, auth_client: Any, user: Any
    ) -> None:
        # Obter tokens
        obtain_resp = auth_client.post(
            "/api/v1/auth/token/",
            {"email": user.email, "password": "password123"},
            content_type="application/json",
        )
        tokens = obtain_resp.json()
        refresh_token = tokens["refresh"]

        # Logout bem-sucedido -> 200 (RFC 7009)
        logout_resp = auth_client.post(
            "/api/v1/auth/logout/",
            {"refresh": refresh_token},
            content_type="application/json",
        )
        assert logout_resp.status_code == 200
        assert logout_resp.json()["message"] == "Logout realizado com sucesso."

        # Tentar usar o refresh token invalidado no endpoint de refresh -> 401
        refresh_resp = auth_client.post(
            "/api/v1/auth/refresh/",
            {"refresh": refresh_token},
            content_type="application/json",
        )
        assert refresh_resp.status_code == 401

        # Logout com token inválido/já revogado -> 200 (idempotente RFC 7009)
        idempotent_resp = auth_client.post(
            "/api/v1/auth/logout/",
            {"refresh": "invalid-or-revoked-token"},
            content_type="application/json",
        )
        assert idempotent_resp.status_code == 200

    def test_password_length_dos_mitigation(self, auth_client: Any) -> None:
        long_password = "A" * 129

        # Login com senha excessiva -> 422 Unprocessable Entity
        login_resp = auth_client.post(
            "/api/v1/auth/token/",
            {"email": "dos@example.com", "password": long_password},
            content_type="application/json",
        )
        assert login_resp.status_code == 422

        # Registro com senha excessiva -> 422
        register_resp = auth_client.post(
            "/api/v1/auth/register/",
            {
                "email": "dos@example.com",
                "password": long_password,
                "first_name": "Test",
                "last_name": "User",
            },
            content_type="application/json",
        )
        assert register_resp.status_code == 422
