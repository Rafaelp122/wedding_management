from django.conf import settings

from .base import OIDCVerifier
from .gcp import GCPOIDCVerifier
from .mock import MockOIDCVerifier


def get_oidc_verifier() -> OIDCVerifier:
    """
    Retorna a implementação ativa do OIDCVerifier com base no ambiente.

    Decisão Arquitetural:
        ADR-005 (docs/architecture/adr/005-oidc-scheduler.md)

    Returns:
        Instância concreta de OIDCVerifier (Mock em testes/desenvolvimento ou GCP em produção).
    """
    is_dev_or_test = getattr(settings, "DEBUG", False) or getattr(
        settings, "TESTING", False
    )
    if is_dev_or_test:
        return MockOIDCVerifier()
    return GCPOIDCVerifier()
