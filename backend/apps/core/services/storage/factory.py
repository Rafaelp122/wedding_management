from django.conf import settings

from apps.core.exceptions import BusinessRuleViolation

from .base import StorageService
from .cloudflare_r2 import CloudflareR2StorageService


def get_storage_service() -> StorageService:
    """
    Retorna a implementação ativa do StorageService.

    A escolha do provedor é feita com base no settings do Django.

    Returns:
        Uma instância concreta de StorageService correspondente.

    Raises:
        BusinessRuleViolation: Se o provedor configurado no settings
            não for suportado.
    """
    provider = getattr(settings, "STORAGE_PROVIDER", "R2").upper()

    if provider == "R2":
        return CloudflareR2StorageService()
    # Outros provedores (como GCS, S3 padrão) podem ser
    # facilmente adicionados aqui no futuro.
    raise BusinessRuleViolation(
        detail=f"Provedor de storage '{provider}' não suportado.",
        code="unsupported_storage_provider",
    )
