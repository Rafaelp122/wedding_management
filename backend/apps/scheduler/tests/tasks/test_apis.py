import pytest

from apps.scheduler.tests.factories import TaskFactory
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
@pytest.mark.api
class TestTaskAPI:
    """Testes de integração para a API de Tarefas - Conforme TESTING_STANDARDS.md."""

    @pytest.mark.multitenancy
    def test_list_tasks_isolation(self, auth_client, user):
        """Garante que um planner só vê tarefas dos seus casamentos."""
        my_wedding = WeddingFactory(planner=user)
        TaskFactory(wedding=my_wedding, title="Minha Tarefa")

        # Tarefa de outro planner
        TaskFactory(title="Tarefa Alheia")

        response = auth_client.get("/api/v1/scheduler/tasks/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == "Minha Tarefa"

    @pytest.mark.security
    @pytest.mark.multitenancy
    def test_retrieve_task_forbidden(self, auth_client):
        """Segurança: Não pode acessar tarefa de outro planner."""
        other_task = TaskFactory()
        response = auth_client.get(f"/api/v1/scheduler/tasks/{other_task.uuid}/")
        assert response.status_code == 404

    def test_create_task_success(self, auth_client, user):
        """Cenário feliz de criação via API."""
        wedding = WeddingFactory(planner=user)
        payload = {
            "wedding": str(wedding.uuid),
            "title": "Degustação",
            "due_date": "2026-10-10",
        }
        response = auth_client.post(
            "/api/v1/scheduler/tasks/", data=payload, content_type="application/json"
        )
        assert response.status_code == 201
        assert response.json()["title"] == "Degustação"

    @pytest.mark.security
    @pytest.mark.multitenancy
    def test_update_task_isolation(self, auth_client):
        """Segurança: Não pode editar tarefa de outro planner."""
        other_task = TaskFactory(title="Original")
        response = auth_client.patch(
            f"/api/v1/scheduler/tasks/{other_task.uuid}/",
            data={"title": "Hack"},
            content_type="application/json",
        )
        assert response.status_code == 404

    @pytest.mark.security
    @pytest.mark.multitenancy
    def test_delete_task_isolation(self, auth_client):
        """Segurança: Não pode deletar tarefa de outro planner."""
        other_task = TaskFactory()
        response = auth_client.delete(f"/api/v1/scheduler/tasks/{other_task.uuid}/")
        assert response.status_code == 404
