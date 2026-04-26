import logging

import pytest

from apps.core.logging import RequestIDFilter, _thread_locals


@pytest.mark.unit
class TestLoggingFilters:
    """Testes para utilitários de logging."""

    def test_request_id_filter_with_id(self):
        """Garante que o filtro injeta o ID do thread local no registro de log."""
        # Setup
        _thread_locals.request_id = "test-123"
        filter_ = RequestIDFilter()
        record = logging.LogRecord("test", logging.INFO, "path", 1, "msg", None, None)

        # Execução
        filter_.filter(record)

        # Asserções
        assert record.request_id == "test-123"

    def test_request_id_filter_without_id_defaults_to_system(self):
        """Garante que assume 'system' quando não há ID no thread local."""
        # Setup
        if hasattr(_thread_locals, "request_id"):
            del _thread_locals.request_id
        filter_ = RequestIDFilter()
        record = logging.LogRecord("test", logging.INFO, "path", 1, "msg", None, None)

        # Execução
        filter_.filter(record)

        # Asserções
        assert record.request_id == "system"
