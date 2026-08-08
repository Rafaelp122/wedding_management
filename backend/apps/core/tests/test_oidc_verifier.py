from unittest.mock import MagicMock, patch

import pytest

from apps.core.services.oidc.gcp import GCPOIDCVerifier
from apps.core.services.oidc.mock import MockOIDCVerifier


class TestOIDCVerifiers:
    """Testes de unidade para os verificadores OIDC."""

    def test_mock_oidc_verifier_valid_token(self) -> None:
        """Verifica se o MockOIDCVerifier valida dev-cron-token."""
        verifier = MockOIDCVerifier()
        claims = verifier.verify_token("dev-cron-token")

        assert claims["email"] == "scheduler-dev@local.iam.gserviceaccount.com"
        assert claims["iss"] == "https://accounts.google.com"

    def test_mock_oidc_verifier_invalid_token_raises_value_error(self) -> None:
        """Verifica se o MockOIDCVerifier lança ValueError para token inválido."""
        verifier = MockOIDCVerifier()
        with pytest.raises(ValueError, match="Token OIDC inválido"):
            verifier.verify_token("invalid-token-123")

    @patch("google.oauth2.id_token.verify_oauth2_token")
    @patch("google.auth.transport.requests.Request")
    def test_gcp_oidc_verifier_success(
        self, mock_request: MagicMock, mock_verify: MagicMock
    ) -> None:
        """Verifica se o GCPOIDCVerifier valida token e SA autorizada."""
        mock_verify.return_value = {
            "email": "scheduler-sa@project.iam.gserviceaccount.com",
            "aud": "https://api.meunoivado.com",
        }

        verifier = GCPOIDCVerifier(
            audience="https://api.meunoivado.com",
            expected_service_account="scheduler-sa@project.iam.gserviceaccount.com",
        )

        claims = verifier.verify_token("valid-gcp-token")

        assert claims["email"] == "scheduler-sa@project.iam.gserviceaccount.com"
        mock_verify.assert_called_once()

    @patch("google.oauth2.id_token.verify_oauth2_token")
    @patch("google.auth.transport.requests.Request")
    def test_gcp_oidc_verifier_unauthorized_service_account(
        self, mock_request: MagicMock, mock_verify: MagicMock
    ) -> None:
        """Verifica se o GCPOIDCVerifier lança PermissionError em SA diferente."""
        mock_verify.return_value = {
            "email": "hacker-sa@project.iam.gserviceaccount.com",
            "aud": "https://api.meunoivado.com",
        }

        verifier = GCPOIDCVerifier(
            audience="https://api.meunoivado.com",
            expected_service_account="scheduler-sa@project.iam.gserviceaccount.com",
        )

        with pytest.raises(PermissionError, match="Service account não autorizada"):
            verifier.verify_token("valid-gcp-token-wrong-sa")
