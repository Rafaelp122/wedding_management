import logging

from .base import OIDCClaims


logger = logging.getLogger(__name__)


class MockOIDCVerifier:
    """
    Implementação mock do OIDCVerifier para Dev e Testes (Pytest).
    """

    def verify_token(self, token: str) -> OIDCClaims:
        """
        Retorna claims simuladas para ambiente de testes e desenvolvimento.

        Args:
            token: O token recebido na requisição.

        Returns:
            Dicionário com as claims simuladas da service account.

        Raises:
            ValueError: Se o token for inválido no ambiente mock.
        """
        dev_token = "dev-cron-token"  # noqa: S105 # pragma: allowlist secret
        if token == dev_token:
            return {
                "iss": "https://accounts.google.com",
                "aud": "http://localhost:8000",
                "email": "scheduler-dev@local.iam.gserviceaccount.com",
            }
        logger.warning("MockOIDCVerifier rejeitou o token OIDC inválido.")
        raise ValueError("Token OIDC inválido.")
