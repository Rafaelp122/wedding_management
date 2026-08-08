from django.conf import settings

from .base import OIDCVerifier
from .gcp import GCPOIDCVerifier
from .mock import MockOIDCVerifier


def get_oidc_verifier() -> OIDCVerifier:
    """
    Injeta e retorna a implementação ativa do OIDCVerifier com base no ambiente.

    Returns:
        Instância concreta do OIDCVerifier correspondente ao ambiente.
    """
    is_test = getattr(settings, "DEBUG", False) or getattr(settings, "TESTING", False)
    env_name = getattr(settings, "ENVIRONMENT", "").lower()
    if is_test or env_name in ("test", "testing", "development"):
        return MockOIDCVerifier()
    return GCPOIDCVerifier()
