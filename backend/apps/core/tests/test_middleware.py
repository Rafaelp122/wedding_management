from unittest.mock import patch

from django.http import HttpRequest, HttpResponse

from apps.core.middleware import RequestIDMiddleware


class TestRequestIDMiddleware:
    def test_generates_request_id_when_none_provided(self):
        def get_response(request: HttpRequest) -> HttpResponse:
            return HttpResponse("ok")

        middleware = RequestIDMiddleware(get_response)
        request = HttpRequest()
        request.META = {}

        response = middleware(request)

        assert "X-Request-ID" in response
        assert response["X-Request-ID"]

    def test_uses_provided_request_id_header(self):
        def get_response(request: HttpRequest) -> HttpResponse:
            return HttpResponse("ok")

        middleware = RequestIDMiddleware(get_response)
        request = HttpRequest()
        request.META = {}
        request.headers = {"X-Request-ID": "custom-id-123"}

        response = middleware(request)

        assert response["X-Request-ID"] == "custom-id-123"

    @patch("apps.core.middleware.sentry_sdk.set_context")
    def test_sets_sentry_context_with_request_id(self, mock_set_context):
        def get_response(request: HttpRequest) -> HttpResponse:
            return HttpResponse("ok")

        middleware = RequestIDMiddleware(get_response)
        request = HttpRequest()
        request.META = {}
        request.headers = {"X-Request-ID": "test-id-456"}

        middleware(request)

        mock_set_context.assert_called_once_with(
            "request", {"request_id": "test-id-456"}
        )

    @patch("apps.core.middleware.sentry_sdk.set_context")
    def test_sets_sentry_context_with_generated_id(self, mock_set_context):
        def get_response(request: HttpRequest) -> HttpResponse:
            return HttpResponse("ok")

        middleware = RequestIDMiddleware(get_response)
        request = HttpRequest()
        request.META = {}

        middleware(request)

        mock_set_context.assert_called_once()
        call_args = mock_set_context.call_args
        assert call_args[0][0] == "request"
        assert "request_id" in call_args[0][1]
