from django.db.models import QuerySet
from django.http import HttpRequest
from ninja import Router
from ninja.pagination import paginate
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES
from apps.scheduler.models import Task
from apps.scheduler.schemas import TaskIn, TaskOut, TaskPatchIn
from apps.scheduler.services import TaskService


tasks_router = Router(tags=["Scheduler"])


@tasks_router.get("/", response=list[TaskOut], operation_id="scheduler_tasks_list")
@paginate
def list_tasks(request: HttpRequest, wedding_id: UUID4 | None = None) -> QuerySet[Task]:
    """
    Lista tarefas e checklist.
    """
    return TaskService.list(request.user.company, wedding_id=wedding_id)


@tasks_router.post(
    "/",
    response={201: TaskOut, **MUTATION_ERROR_RESPONSES},
    operation_id="scheduler_tasks_create",
)
def create_task(request: HttpRequest, payload: TaskIn) -> tuple[int, Task]:
    """
    Cria uma nova tarefa no checklist.
    """
    return 201, TaskService.create(request.user.company, payload.dict())


@tasks_router.patch(
    "/{uuid}/",
    response={200: TaskOut, **MUTATION_ERROR_RESPONSES},
    operation_id="scheduler_tasks_update",
)
def update_task(request: HttpRequest, uuid: UUID4, payload: TaskPatchIn) -> Task:
    """
    Atualiza uma tarefa (incluindo marcação de conclusão se `is_completed` for passado).
    """
    instance = TaskService.get(request.user.company, uuid)
    return TaskService.update(
        request.user.company, instance, payload.dict(exclude_unset=True)
    )


@tasks_router.delete(
    "/{uuid}/",
    response={204: None, **MUTATION_ERROR_RESPONSES},
    operation_id="scheduler_tasks_delete",
)
def delete_task(request: HttpRequest, uuid: UUID4) -> tuple[int, None]:
    """
    Remove uma tarefa permanentemente.
    """
    TaskService.delete(request.user.company, uuid)
    return 204, None
