from django.db.models import QuerySet
from ninja.pagination import paginate
from ninja_extra import (
    ControllerBase,
    api_controller,
    http_delete,
    http_get,
    http_patch,
    http_post,
)
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES
from apps.scheduler.models import Task
from apps.scheduler.schemas import (
    TaskIn,
    TaskOut,
    TaskPatchIn,
)
from apps.scheduler.services import TaskService


@api_controller("/scheduler/tasks", tags=["Scheduler"])
class TaskController(ControllerBase):
    def __init__(self, service: TaskService):
        self.service = service

    @http_get("/", response=list[TaskOut], operation_id="scheduler_tasks_list")
    @paginate
    def list_tasks(self, wedding_id: UUID4 | None = None) -> QuerySet[Task]:
        """
        Lista tarefas e checklist.
        """
        return self.service.list(self.context.request.user, wedding_id=wedding_id)

    @http_post(
        "/",
        response={201: TaskOut, **MUTATION_ERROR_RESPONSES},
        operation_id="scheduler_tasks_create",
    )
    def create_task(self, payload: TaskIn) -> tuple[int, Task]:
        """
        Cria uma nova tarefa no checklist.
        """
        task = self.service.create(self.context.request.user, payload.model_dump())
        return 201, task

    @http_patch(
        "/{uuid}/",
        response={200: TaskOut, **MUTATION_ERROR_RESPONSES},
        operation_id="scheduler_tasks_partial_update",
    )
    def partial_update_task(self, uuid: UUID4, payload: TaskPatchIn) -> Task:
        """
        Atualiza uma tarefa (incluindo marcação de conclusão).
        """
        instance = self.service.get(self.context.request.user, uuid=uuid)
        return self.service.partial_update(
            self.context.request.user, instance, payload.model_dump(exclude_unset=True)
        )

    @http_delete(
        "/{uuid}/",
        response={204: None, **MUTATION_ERROR_RESPONSES},
        operation_id="scheduler_tasks_delete",
    )
    def delete_task(self, uuid: UUID4) -> tuple[int, None]:
        """
        Remove uma tarefa permanentemente.
        """
        self.service.delete(self.context.request.user, uuid)
        return 204, None
