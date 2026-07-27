"""
Testes de consistência do envelope de erros da API Ninja.

Garante que 100% das respostas de erro da API (400, 401, 403, 404, 409, 422, 500)
retornam uma estrutura JSON válida contendo obrigatoriamente as chaves
'detail' e 'code' ({"detail": ..., "code": ...}).
"""

import uuid
from typing import NoReturn

import pytest
from django.test import Client
from ninja_jwt.tokens import RefreshToken

from apps.users.models import User
from apps.users.tests.factories import UserFactory


def _get_auth_headers(user: User) -> dict[str, str]:
    """Retorna os cabeçalhos HTTP com token Bearer válido para o usuário."""
    refresh = RefreshToken.for_user(user)
    access_token = str(getattr(refresh, "access_token", refresh))
    return {"HTTP_AUTHORIZATION": f"Bearer {access_token}"}


@pytest.mark.django_db
class TestErrorEnvelopeConsistency:
    """
    Suíte de testes para validação do padrão uniforme de erro da API.
    """

    def test_401_unauthorized_error_envelope(self, client: Client) -> None:
        """
        Garante que requisições não autenticadas (HTTP 401) retornam um JSON
        padronizado com 'detail' e 'code'.
        """
        response = client.get("/api/v1/weddings/")
        assert response.status_code == 401

        data = response.json()
        assert isinstance(data, dict), f"Resposta 401 não é um objeto JSON: {data}"
        assert "detail" in data, "Resposta 401 não contém a chave 'detail'."
        assert "code" in data, "Resposta 401 não contém a chave 'code'."
        assert data["code"] == "unauthorized"

    def test_403_forbidden_error_envelope(
        self, client: Client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        Garante que erros de permissão/acesso negado (HTTP 403) retornam um JSON
        padronizado com 'detail' e 'code'.
        """
        user = UserFactory()
        headers = _get_auth_headers(user)

        def _mock_forbidden(*args: object, **kwargs: object) -> NoReturn:
            from ninja.errors import HttpError

            raise HttpError(403, "Acesso negado para este recurso.")

        monkeypatch.setattr(
            "apps.weddings.services.wedding_service.WeddingService.list",
            _mock_forbidden,
        )

        response = client.get(
            "/api/v1/weddings/",
            **headers,
        )
        assert response.status_code == 403

        data = response.json()
        assert isinstance(data, dict), f"Resposta 403 não é um objeto JSON: {data}"
        assert "detail" in data, "Resposta 403 não contém a chave 'detail'."
        assert "code" in data, "Resposta 403 não contém a chave 'code'."
        assert data["code"] == "forbidden"

    def test_404_not_found_error_envelope(self, client: Client) -> None:
        """
        Garante que recursos não encontrados (HTTP 404) retornam um JSON
        padronizado com 'detail' e 'code'.
        """
        user = UserFactory()
        headers = _get_auth_headers(user)
        random_uuid = str(uuid.uuid4())

        response = client.get(
            f"/api/v1/weddings/{random_uuid}/",
            **headers,
        )
        assert response.status_code == 404

        data = response.json()
        assert isinstance(data, dict), f"Resposta 404 não é um objeto JSON: {data}"
        assert "detail" in data, "Resposta 404 não contém a chave 'detail'."
        assert "code" in data, "Resposta 404 não contém a chave 'code'."
        assert data["code"] == "not_found"

    def test_409_conflict_error_envelope(
        self, client: Client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        Garante que erros de conflito/integridade de domínio
        (HTTP 409 / DomainIntegrityError) retornam JSON padronizado.
        """
        user = UserFactory()
        headers = _get_auth_headers(user)

        def _mock_conflict(*args: object, **kwargs: object) -> NoReturn:
            from apps.core.exceptions import DomainIntegrityError

            raise DomainIntegrityError(
                detail="Conflito de integridade de dados no domínio.",
                code="domain_conflict_error",
            )

        monkeypatch.setattr(
            "apps.weddings.services.wedding_service.WeddingService.list",
            _mock_conflict,
        )

        response = client.get(
            "/api/v1/weddings/",
            **headers,
        )
        assert response.status_code == 409

        data = response.json()
        assert isinstance(data, dict), f"Resposta 409 não é um objeto JSON: {data}"
        assert "detail" in data, "Resposta 409 não contém a chave 'detail'."
        assert "code" in data, "Resposta 409 não contém a chave 'code'."
        assert data["code"] == "domain_conflict_error"

    def test_422_validation_error_envelope(self, client: Client) -> None:
        """
        Garante que erros de validação de payload (HTTP 422) retornam um JSON
        padronizado com 'detail' e 'code'.
        """
        response = client.post(
            "/api/v1/auth/token/",
            data={},
            content_type="application/json",
        )
        assert response.status_code == 422

        data = response.json()
        assert isinstance(data, dict), f"Resposta 422 não é um objeto JSON: {data}"
        assert "detail" in data, "Resposta 422 não contém a chave 'detail'."
        assert "code" in data, "Resposta 422 não contém a chave 'code'."
        assert data["code"] == "validation_error"

    def test_400_bad_request_error_envelope(self, client: Client) -> None:
        """
        Garante que requisições com formato malformado ou Bad Request (HTTP 400)
        retornam um JSON padronizado com 'detail' e 'code'.
        """
        response = client.post(
            "/api/v1/auth/token/",
            data="invalid json{",
            content_type="application/json",
        )
        assert response.status_code == 400

        data = response.json()
        assert isinstance(data, dict), f"Resposta 400 não é um objeto JSON: {data}"
        assert "detail" in data, "Resposta 400 não contém a chave 'detail'."
        assert "code" in data, "Resposta 400 não contém a chave 'code'."

    def test_500_internal_server_error_envelope(
        self, client: Client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        Garante que erros internos não previstos (HTTP 500) retornam um JSON
        padronizado com 'detail' e 'code'.
        """
        user = UserFactory()
        headers = _get_auth_headers(user)

        def _mock_crash(*args: object, **kwargs: object) -> NoReturn:
            raise RuntimeError("Falha interna simulada para teste de 500.")

        monkeypatch.setattr(
            "apps.weddings.services.wedding_service.WeddingService.list",
            _mock_crash,
        )

        response = client.get(
            "/api/v1/weddings/",
            **headers,
        )
        assert response.status_code == 500

        data = response.json()
        assert isinstance(data, dict), f"Resposta 500 não é um objeto JSON: {data}"
        assert "detail" in data, "Resposta 500 não contém a chave 'detail'."
        assert "code" in data, "Resposta 500 não contém a chave 'code'."
        assert data["code"] == "internal_error"
