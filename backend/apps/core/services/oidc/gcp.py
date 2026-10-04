import logging
from typing import cast

from django.conf import settings

from .base import OIDCClaims


logger = logging.getLogger(__name__)


class GCPOIDCVerifier:
    """
    Implementação concreta de OIDCVerifier para o GCP (Cloud Scheduler e Cloud Run).

    Decisão Arquitetural:
        ADR-005 (docs/architecture/adr/005-oidc-scheduler.md)
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

    def verify_token(self, token: str) -> OIDCClaims:
        """
        Valida o token OIDC criptograficamente contra o emissor Google.

        Decisão Arquitetural:
            ADR-005 (docs/architecture/adr/005-oidc-scheduler.md)

        Args:
            token: Token JWT assinado pela conta de serviço da nuvem.

        Returns:
            Dicionário contendo as claims validadas pelo emissor Google.

        Raises:
            PermissionError: Se a conta de serviço do emissor não for autorizada.
            ValueError: Se o token for inválido, expirado ou com audience incompatível.
        """
        from google.auth.transport import requests as google_requests
        from google.oauth2 import id_token

        claim = cast(
            OIDCClaims,
            id_token.verify_oauth2_token(  # type: ignore[no-untyped-call]
                token,
                google_requests.Request(),
                audience=self.audience,
            ),
        )

        if (
            self.expected_service_account
            and claim.get("email") != self.expected_service_account
        ):
            logger.warning("OIDC Error: Service account não autorizada.")
            msg = "Service account não autorizada."
            raise PermissionError(msg)

        return claim
