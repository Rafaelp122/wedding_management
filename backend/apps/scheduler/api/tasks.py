from django.db.models import QuerySet
from ninja.pagination import paginate
from ninja_extra import Router
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES
from apps.scheduler.models import Task
from apps.scheduler.schemas import TaskIn, TaskOut, TaskPatchIn
from apps.scheduler.selectors import task_get_selector, task_list_selector
from apps.scheduler.services import TaskService
from apps.users.types import AuthRequest


tasks_router = Router(tags=["Scheduler"])


@tasks_router.get("/", response=list[TaskOut], operation_id="scheduler_tasks_list")
@paginate
def list_tasks(
    request: AuthRequest,
    wedding_id: UUID4 | None = None,
) -> QuerySet[Task]:
    """Lista tarefas do checklist com filtros opcionais por casamento."""
    user = request.user
    return task_list_selector(
        company=user.company,
        wedding_id=wedding_id,
    )


@tasks_router.post(
    "/",
    response={201: TaskOut, **MUTATION_ERROR_RESPONSES},
    operation_id="scheduler_tasks_create",
)
def create_task(request: AuthRequest, payload: TaskIn) -> tuple[int, Task]:
    """Cria uma nova tarefa no checklist do casamento."""
    user = request.user
    created = TaskService.create(user.company, payload)
    return 201, task_get_selector(company=user.company, uuid=created.uuid)


@tasks_router.patch(
    "/{uuid}/",
    response={200: TaskOut, **MUTATION_ERROR_RESPONSES},
    operation_id="scheduler_tasks_update",
)
def update_task(request: AuthRequest, uuid: UUID4, payload: TaskPatchIn) -> Task:
    """Atualiza os dados de uma tarefa existente no checklist."""
    user = request.user
    instance = task_get_selector(company=user.company, uuid=uuid)
    updated = TaskService.update(user.company, instance, payload)
    return task_get_selector(company=user.company, uuid=updated.uuid)


@tasks_router.post(
    "/{uuid}/complete/",
    response={200: TaskOut, **MUTATION_ERROR_RESPONSES},
    operation_id="scheduler_tasks_complete",
)
def complete_task(request: AuthRequest, uuid: UUID4) -> Task:
    """Marca uma tarefa do checklist como concluída."""
    user = request.user
    instance = task_get_selector(company=user.company, uuid=uuid)
    completed = TaskService.complete(user.company, instance)
    return task_get_selector(company=user.company, uuid=completed.uuid)


@tasks_router.post(
    "/{uuid}/reopen/",
    response={200: TaskOut, **MUTATION_ERROR_RESPONSES},
    operation_id="scheduler_tasks_reopen",
)
def reopen_task(request: AuthRequest, uuid: UUID4) -> Task:
    """Reabre uma tarefa previamente concluída do checklist."""
    user = request.user
    instance = task_get_selector(company=user.company, uuid=uuid)
    reopened = TaskService.reopen(user.company, instance)
    return task_get_selector(company=user.company, uuid=reopened.uuid)


@tasks_router.delete(
    "/{uuid}/",
    response={204: None, **MUTATION_ERROR_RESPONSES},
    operation_id="scheduler_tasks_delete",
)
def delete_task(request: AuthRequest, uuid: UUID4) -> tuple[int, None]:
    """Remove uma tarefa existente do checklist."""
    user = request.user
    instance = task_get_selector(company=user.company, uuid=uuid)
    TaskService.delete(user.company, instance)
    return 204, None
