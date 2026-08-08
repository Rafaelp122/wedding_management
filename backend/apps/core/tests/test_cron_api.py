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
