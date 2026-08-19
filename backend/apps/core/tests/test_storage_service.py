from typing import Any
from unittest.mock import patch

import pytest

from apps.core.exceptions import BusinessRuleViolation
from apps.core.services.storage import (
    CloudflareR2StorageService,
    get_storage_service,
)


class TestCloudflareR2StorageService:
    """Testes unitários isolados do CloudflareR2StorageService."""

    @patch("boto3.client")
    def test_generate_presigned_put_url_success(
        self, mock_boto3_client: Any, settings: Any
    ) -> None:
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

    @patch("boto3.client")
    def test_generate_presigned_get_url_success(
        self, mock_boto3_client: Any, settings: Any
    ) -> None:
        settings.R2_ENDPOINT_URL = "https://r2-endpoint.com"
        settings.R2_ACCESS_KEY_ID = "test-key-id"
        settings.R2_SECRET_ACCESS_KEY = "test-secret-key"
        settings.AWS_S3_ENDPOINT_URL = "https://r2-endpoint.com"
        settings.AWS_ACCESS_KEY_ID = "test-key-id"
        settings.AWS_SECRET_ACCESS_KEY = "test-secret-key"

        mock_s3 = mock_boto3_client.return_value
        mock_s3.generate_presigned_url.return_value = "https://r2.com/download-url"

        storage = CloudflareR2StorageService()
        url = storage.generate_presigned_get_url(
            bucket="test-bucket",
            object_key="test-key",
            expires_in=600,
        )

        assert url == "https://r2.com/download-url"
        mock_s3.generate_presigned_url.assert_called_once_with(
            "get_object",
            Params={
                "Bucket": "test-bucket",
                "Key": "test-key",
            },
            ExpiresIn=600,
        )

    @patch("boto3.client")
    def test_upload_bytes_success(self, mock_boto3_client: Any, settings: Any) -> None:
        settings.R2_ENDPOINT_URL = "https://r2-endpoint.com"
        settings.R2_ACCESS_KEY_ID = "test-key-id"
        settings.R2_SECRET_ACCESS_KEY = "test-secret-key"
        settings.AWS_S3_ENDPOINT_URL = "https://r2-endpoint.com"
        settings.AWS_ACCESS_KEY_ID = "test-key-id"
        settings.AWS_SECRET_ACCESS_KEY = "test-secret-key"

        mock_s3 = mock_boto3_client.return_value

        storage = CloudflareR2StorageService()
        key = storage.upload_bytes(
            bucket="test-bucket",
            object_key="reports/relatorio.pdf",
            data=b"pdf-content",
            content_type="application/pdf",
        )

        assert key == "reports/relatorio.pdf"
        mock_s3.put_object.assert_called_once_with(
            Bucket="test-bucket",
            Key="reports/relatorio.pdf",
            Body=b"pdf-content",
            ContentType="application/pdf",
        )

    def test_generate_presigned_put_url_configuration_incomplete(
        self, settings: Any
    ) -> None:
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

    def test_generate_presigned_get_url_configuration_incomplete(
        self, settings: Any
    ) -> None:
        settings.R2_ENDPOINT_URL = ""
        settings.AWS_S3_ENDPOINT_URL = ""

        storage = CloudflareR2StorageService()
        with pytest.raises(BusinessRuleViolation) as exc_info:
            storage.generate_presigned_get_url(
                bucket="test-bucket",
                object_key="test-key",
            )
        assert exc_info.value.code == "storage_configuration_incomplete"

    def test_upload_bytes_configuration_incomplete(self, settings: Any) -> None:
        settings.R2_ENDPOINT_URL = ""
        settings.AWS_S3_ENDPOINT_URL = ""

        storage = CloudflareR2StorageService()
        with pytest.raises(BusinessRuleViolation) as exc_info:
            storage.upload_bytes(
                bucket="test-bucket",
                object_key="test-key",
                data=b"test",
                content_type="application/pdf",
            )
        assert exc_info.value.code == "storage_configuration_incomplete"


class TestGetStorageService:
    """Testes da factory function get_storage_service."""

    def test_get_storage_service_r2_success(self, settings: Any) -> None:
        settings.STORAGE_PROVIDER = "R2"
        service = get_storage_service()
        assert isinstance(service, CloudflareR2StorageService)

    def test_get_storage_service_unsupported_raises_error(self, settings: Any) -> None:
        settings.STORAGE_PROVIDER = "GCS"
        with pytest.raises(BusinessRuleViolation) as exc_info:
            get_storage_service()
        assert exc_info.value.code == "unsupported_storage_provider"
