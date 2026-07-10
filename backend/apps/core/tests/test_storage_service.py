from unittest.mock import patch

import pytest

from apps.core.exceptions import BusinessRuleViolation
from apps.core.services.storage_service import (
    CloudflareR2StorageService,
    get_storage_service,
)


class TestCloudflareR2StorageService:
    """Testes unitários isolados do CloudflareR2StorageService."""

    @patch("boto3.client")
    def test_generate_presigned_put_url_success(self, mock_boto3_client, settings):
        settings.R2_ENDPOINT_URL = "https://r2-endpoint.com"
        settings.R2_ACCESS_KEY_ID = "test-key-id"
        settings.R2_SECRET_ACCESS_KEY = "test-secret-key"
        settings.AWS_S3_ENDPOINT_URL = "https://r2-endpoint.com"
        settings.AWS_ACCESS_KEY_ID = "test-key-id"
        settings.AWS_SECRET_ACCESS_KEY = "test-secret-key"

        mock_s3 = mock_boto3_client.return_value
        mock_s3.generate_presigned_url.return_value = "https://r2.com/presigned-url"

        storage = CloudflareR2StorageService()
        url = storage.generate_presigned_put_url(
            bucket="test-bucket",
            object_key="test-key",
            content_type="application/pdf",
        )

        assert url == "https://r2.com/presigned-url"
        mock_boto3_client.assert_called_once_with(
            "s3",
            endpoint_url="https://r2-endpoint.com",
            aws_access_key_id="test-key-id",
            aws_secret_access_key="test-secret-key",
            region_name="us-east-1",
        )
        mock_s3.generate_presigned_url.assert_called_once_with(
            "put_object",
            Params={
                "Bucket": "test-bucket",
                "Key": "test-key",
                "ContentType": "application/pdf",
            },
            ExpiresIn=900,
        )

    def test_generate_presigned_put_url_configuration_incomplete(self, settings):
        settings.R2_ENDPOINT_URL = ""
        settings.AWS_S3_ENDPOINT_URL = ""

        storage = CloudflareR2StorageService()
        with pytest.raises(BusinessRuleViolation) as exc_info:
            storage.generate_presigned_put_url(
                bucket="test-bucket",
                object_key="test-key",
                content_type="application/pdf",
            )
        assert exc_info.value.code == "storage_configuration_incomplete"


class TestGetStorageService:
    """Testes da factory function get_storage_service."""

    def test_get_storage_service_r2_success(self, settings):
        settings.STORAGE_PROVIDER = "R2"
        service = get_storage_service()
        assert isinstance(service, CloudflareR2StorageService)

    def test_get_storage_service_unsupported_raises_error(self, settings):
        settings.STORAGE_PROVIDER = "GCS"
        with pytest.raises(BusinessRuleViolation) as exc_info:
            get_storage_service()
        assert exc_info.value.code == "unsupported_storage_provider"
