import logging
from typing import Any


logger = logging.getLogger(__name__)


class MockOIDCVerifier:
    """
    Implementação mock do OIDCVerifier para Dev e Testes (Pytest).
    """

    def verify_token(self, token: str) -> dict[str, Any]:
        """
        Retorna claims simuladas para ambiente de testes e desenvolvimento.

        Args:
            token: O token fake recebido nos testes.

        Returns:
            Dicionário com as claims simuladas da service account.
        """
        dev_token = "dev-cron-token"  # noqa: S105 # pragma: allowlist secret
        if token == dev_token or not token:
            return {
                "iss": "https://accounts.google.com",
                "aud": "http://localhost:8000",
                "email": "scheduler-dev@local.iam.gserviceaccount.com",
            }
        logger.info("MockOIDCVerifier aceitou o token em ambiente local/dev: %s", token)
        return {
            "iss": "mock-issuer",
            "aud": "mock-audience",
            "email": "mock-scheduler@local.iam.gserviceaccount.com",
        }
