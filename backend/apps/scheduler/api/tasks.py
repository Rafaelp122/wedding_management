from django.db.models import QuerySet
from ninja import Router
from ninja.pagination import paginate
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES
from apps.scheduler.models import Task
from apps.scheduler.schemas import TaskIn, TaskOut, TaskPatchIn
from apps.scheduler.services import TaskService
from apps.users.auth import require_user
from apps.users.types import AuthRequest


tasks_router = Router(tags=["Scheduler"])


@tasks_router.get("/", response=list[TaskOut], operation_id="scheduler_tasks_list")
@paginate
def list_tasks(request: AuthRequest, wedding_id: UUID4 | None = None) -> QuerySet[Task]:
    """
    Lista tarefas e checklist.
    """
    user = require_user(request.user)
    return TaskService.list(user.company, wedding_id=wedding_id)


@tasks_router.post(
    "/",
    response={201: TaskOut, **MUTATION_ERROR_RESPONSES},
    operation_id="scheduler_tasks_create",
)
def create_task(request: AuthRequest, payload: TaskIn) -> tuple[int, Task]:
    """
    Cria uma nova tarefa no checklist.
    """
    user = require_user(request.user)
    return 201, TaskService.create(user.company, payload.dict())


@tasks_router.patch(
    "/{uuid}/",
    response={200: TaskOut, **MUTATION_ERROR_RESPONSES},
    operation_id="scheduler_tasks_update",
)
def update_task(request: AuthRequest, uuid: UUID4, payload: TaskPatchIn) -> Task:
    """
    Atualiza uma tarefa (incluindo marcação de conclusão se `is_completed` for passado).
    """
    user = require_user(request.user)
    instance = TaskService.get(user.company, uuid)
    return TaskService.update(user.company, instance, payload.dict(exclude_unset=True))


@tasks_router.delete(
    "/{uuid}/",
    response={204: None, **MUTATION_ERROR_RESPONSES},
    operation_id="scheduler_tasks_delete",
)
def delete_task(request: AuthRequest, uuid: UUID4) -> tuple[int, None]:
    """
    Remove uma tarefa permanentemente.
    """
    user = require_user(request.user)
    TaskService.delete(user.company, uuid)
    return 204, None
