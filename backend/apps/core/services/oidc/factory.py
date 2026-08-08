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
    is_dev_or_test = getattr(settings, "DEBUG", False) or getattr(
        settings, "TESTING", False
    )
    if is_dev_or_test:
        return MockOIDCVerifier()
    return GCPOIDCVerifier()
