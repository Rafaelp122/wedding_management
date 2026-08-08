import logging
from typing import Any

from django.conf import settings


logger = logging.getLogger(__name__)


class GCPOIDCVerifier:
    """
    Implementação concreta do OIDCVerifier para o GCP (Cloud Scheduler / Cloud Run).
    """

    def __init__(
        self,
        audience: str | None = None,
        expected_service_account: str | None = None,
    ) -> None:
        self.audience = audience or getattr(settings, "CLOUD_RUN_SERVICE_URL", None)
        self.expected_service_account = expected_service_account or getattr(
            settings, "SCHEDULER_SERVICE_ACCOUNT", None
        )

    def verify_token(self, token: str) -> dict[str, Any]:
        """
        Valida o token OIDC criptograficamente contra o emissor Google.

        Args:
            token: O token JWT assinado pela conta de serviço da nuvem.

        Returns:
            Dicionário contendo as claims validadas.

        Raises:
            PermissionError: Se a service account não for autorizada.
        """
        from google.auth.transport import requests as google_requests
        from google.oauth2 import id_token

        claim = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            audience=self.audience,
        )

        if (
            self.expected_service_account
            and claim.get("email") != self.expected_service_account
        ):
            logger.warning(
                "OIDC Error: SA %s não autorizada (esperado: %s)",
                claim.get("email"),
                self.expected_service_account,
            )
            msg = f"Service account não autorizada: {claim.get('email')}"
            raise PermissionError(msg)

        return claim
