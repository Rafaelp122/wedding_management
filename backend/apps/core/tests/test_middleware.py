import uuid

import pytest
from django.http import HttpResponse

from apps.core.logging import get_request_id
from apps.core.middleware import RequestIDMiddleware


@pytest.mark.django_db
class TestRequestIDMiddleware:
    def test_adds_request_id_to_response_header(self, rf):
        """Garante que o middleware adiciona X-Request-ID na resposta."""

        def get_response(req):
            return HttpResponse()

        # Setup
        request = rf.get("/")
        middleware = RequestIDMiddleware(get_response)

        # Execução
        response = middleware(request)

        # Asserção
        assert "X-Request-ID" in response.headers
        assert response.headers["X-Request-ID"] is not None

    def test_uses_existing_request_id_from_header(self, rf):
        """Garante que o middleware reutiliza um ID enviado pelo cliente."""

        def get_response(req):
            return HttpResponse()

        request_id = "test-id-123"
        request = rf.get("/", HTTP_X_REQUEST_ID=request_id)
        middleware = RequestIDMiddleware(get_response)

        # Execução
        response = middleware(request)

        # Asserção
        assert response.headers["X-Request-ID"] == request_id

    def test_request_id_stored_in_thread_local(self, rf):
        """Garante que o ID é armazenado no thread local para logs."""

        def get_response(req):
            return HttpResponse()

        request = rf.get("/")
        middleware = RequestIDMiddleware(get_response)

        # Execução
        middleware(request)

        # Asserção
        assert get_request_id() is not None
        assert isinstance(uuid.UUID(get_request_id()), uuid.UUID)
