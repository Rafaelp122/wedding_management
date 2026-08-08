from unittest.mock import MagicMock, patch

from config.settings.development import _is_redis_available


class TestCacheFallbackRegression:
    """Testes de regressão para o fallback gracioso de cache Redis/LocMem."""

    @patch("socket.create_connection")
    def test_redis_available_returns_true_when_socket_connects(
        self, mock_connect: MagicMock
    ) -> None:
        """Verifica se _is_redis_available retorna True com socket online."""
        mock_connect.return_value.__enter__.return_value = MagicMock()
        assert _is_redis_available("redis://localhost:6379") is True

    @patch("socket.create_connection", side_effect=OSError("Connection refused"))
    def test_redis_available_returns_false_when_socket_fails(
        self, mock_connect: MagicMock
    ) -> None:
        """Verifica se _is_redis_available retorna False com Redis offline."""
        assert _is_redis_available("redis://localhost:6379") is False
