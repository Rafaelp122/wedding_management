from typing import Protocol

import boto3  # type: ignore[import-untyped]
from django.conf import settings

from apps.core.exceptions import BusinessRuleViolation


class StorageService(Protocol):
    """Protocolo definindo a interface para serviços de armazenamento de arquivos."""

    def generate_presigned_put_url(
        self, bucket: str, object_key: str, content_type: str, expires_in: int = 900
    ) -> str:
        """Gera uma URL pré-assinada para upload direto via PUT."""
        ...


class CloudflareR2StorageService:
    """Implementação concreta de StorageService usando Cloudflare R2/S3 via boto3."""

    def __init__(
        self,
        endpoint_url: str | None = None,
        access_key_id: str | None = None,
        secret_access_key: str | None = None,
        region_name: str = "us-east-1",
    ):
        self._endpoint_url = endpoint_url
        self._access_key_id = access_key_id
        self._secret_access_key = secret_access_key
        self.region_name = region_name

    @property
    def endpoint_url(self) -> str | None:
        return (
            self._endpoint_url
            or getattr(settings, "AWS_S3_ENDPOINT_URL", None)
            or getattr(settings, "R2_ENDPOINT_URL", None)
        )

    @property
    def access_key_id(self) -> str | None:
        return (
            self._access_key_id
            or getattr(settings, "AWS_ACCESS_KEY_ID", None)
            or getattr(settings, "R2_ACCESS_KEY_ID", None)
        )

    @property
    def secret_access_key(self) -> str | None:
        return (
            self._secret_access_key
            or getattr(settings, "AWS_SECRET_ACCESS_KEY", None)
            or getattr(settings, "R2_SECRET_ACCESS_KEY", None)
        )

    def generate_presigned_put_url(
        self, bucket: str, object_key: str, content_type: str, expires_in: int = 900
    ) -> str:
        """
        Gera uma URL pré-assinada para upload de um objeto.
        """
        if not all(
            [self.endpoint_url, self.access_key_id, self.secret_access_key, bucket]
        ):
            raise BusinessRuleViolation(
                detail="Configuração de storage R2/S3 incompleta no servidor.",
                code="storage_configuration_incomplete",
            )

        s3_client = boto3.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            region_name=self.region_name,
        )

        presigned_url: str = s3_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": bucket,
                "Key": object_key,
                "ContentType": content_type,
            },
            ExpiresIn=expires_in,
        )
        return presigned_url


def get_storage_service() -> StorageService:
    """
    Factory function para retornar a implementação ativa do StorageService
    com base no provedor configurado no Django settings.
    """
    provider = getattr(settings, "STORAGE_PROVIDER", "R2").upper()

    if provider == "R2":
        return CloudflareR2StorageService()

    # Outros provedores (como GCS, S3 padrão) podem ser
    # facilmente adicionados aqui no futuro.
    raise ValueError(f"Provedor de storage '{provider}' não suportado.")
