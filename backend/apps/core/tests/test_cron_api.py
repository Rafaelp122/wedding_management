import pytest
from django.test import Client

from apps.core.cron import cron_registry


@pytest.mark.django_db
class TestCronApi:
    """Testes para o router de Cron Diário em Lote (/internal/cron/)."""

    def test_daily_batch_cron_endpoint_success(self, client: Client) -> None:
        """Verifica se o endpoint de batch é executado com sucesso e retorna 200 OK."""
        response = client.post(
            "/api/v1/internal/cron/daily-batch/",
            HTTP_AUTHORIZATION="Bearer dev-cron-token",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert "timestamp" in data
        assert isinstance(data["tasks"], list)

    def test_daily_batch_cron_missing_token_returns_401(self, client: Client) -> None:
        """Verifica se a ausência de token OIDC retorna HTTP 401."""
        response = client.post("/api/v1/internal/cron/daily-batch/")

        assert response.status_code == 401
        data = response.json()
        assert data["code"] == "missing_token"

    def test_daily_batch_cron_invalid_token_returns_403(self, client: Client) -> None:
        """Verifica se um token OIDC inválido retorna HTTP 403."""
        response = client.post(
            "/api/v1/internal/cron/daily-batch/",
            HTTP_AUTHORIZATION="Bearer token-invalido-errado",
        )

        assert response.status_code == 403
        data = response.json()
        assert data["code"] == "invalid_token"

    def test_cron_registry_dynamic_task_execution(self, client: Client) -> None:
        """Verifica execução dinâmica de tarefas registradas no CronRegistry."""
        executed = []

        @cron_registry.register("test_custom_task", description="Tarefa de teste")
        def custom_task() -> str:
            executed.append(True)
            return "Tarefa customizada rodou com sucesso."

        response = client.post(
            "/api/v1/internal/cron/daily-batch/",
            HTTP_AUTHORIZATION="Bearer dev-cron-token",
        )

        assert response.status_code == 200
        data = response.json()
        assert len(executed) == 1

        task_names = [t["task"] for t in data["tasks"]]
        assert "test_custom_task" in task_names

    def test_daily_batch_cron_task_failure_returns_207(self, client: Client) -> None:
        """Verifica se falha em uma tarefa do lote retorna HTTP 207 Multi-Status."""

        @cron_registry.register("failing_task", description="Tarefa que lança exceção")
        def failing_task() -> None:
            raise RuntimeError("Falha intencional de teste no lote")

        response = client.post(
            "/api/v1/internal/cron/daily-batch/",
            HTTP_AUTHORIZATION="Bearer dev-cron-token",
        )

        assert response.status_code == 207
        data = response.json()
        assert data["status"] == "completed_with_errors"

        failing_results = [t for t in data["tasks"] if t["task"] == "failing_task"]
        assert len(failing_results) == 1
        assert failing_results[0]["status"] == "error"
        assert failing_results[0]["message"] == "Erro interno ao executar a tarefa."
