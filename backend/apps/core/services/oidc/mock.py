import logging

from .base import OIDCClaims


logger = logging.getLogger(__name__)


class MockOIDCVerifier:
    """
    Implementação mock de OIDCVerifier para desenvolvimento e testes automatizados.

    Decisão Arquitetural:
        ADR-005 (docs/architecture/adr/005-oidc-scheduler.md)
    """

    def verify_token(self, token: str) -> OIDCClaims:
        """
        Retorna claims simuladas para ambiente de testes e desenvolvimento.

        Decisão Arquitetural:
            ADR-005 (docs/architecture/adr/005-oidc-scheduler.md)

        Args:
            token: Token recebido para validação simulada.

        Returns:
            Dicionário com as claims simuladas da service account.

        Raises:
            ValueError: Se o token fornecido não corresponder ao token de mock configurado.
        """
        dev_token = "dev-cron-token"  # noqa: S105 # pragma: allowlist secret
        if token == dev_token:
            return {
                "iss": "https://accounts.google.com",
                "aud": "http://localhost:8000",
                "email": "scheduler-dev@local.iam.gserviceaccount.com",
            }
        logger.warning("MockOIDCVerifier rejeitou o token OIDC inválido.")
        raise ValueError(
            f"Token OIDC inválido: recebido '{token}', esperado '{dev_token}'."
        )
