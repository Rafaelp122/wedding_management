from typing import Any

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
from ninja_extra.permissions import IsAuthenticated
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.scheduler.dependencies import get_event, get_task
from apps.scheduler.models import Event, Task
from apps.scheduler.schemas import (
    EventIn,
    EventOut,
    EventPatchIn,
    TaskIn,
    TaskOut,
    TaskPatchIn,
)
from apps.scheduler.services.events import EventService
from apps.scheduler.services.tasks import TaskService


@api_controller("/scheduler", tags=["Scheduler"], permissions=[IsAuthenticated])
class SchedulerController(ControllerBase):
    context: Any

    # --- EVENTS ---

    @http_get("/events/", response=list[EventOut], operation_id="scheduler_events_list")
    @paginate
    def list_events(self, wedding_id: UUID4 | None = None) -> QuerySet[Event]:
        return EventService.list(self.context.request.user, wedding_id=wedding_id)

    @http_get(
        "/events/{event_uuid}/",
        response={200: EventOut, **READ_ERROR_RESPONSES},
        operation_id="scheduler_events_read",
    )
    def get_event(self, event_uuid: UUID4):
        return get_event(self.context.request, event_uuid)

    @http_post(
        "/events/",
        response={201: EventOut, **MUTATION_ERROR_RESPONSES},
        operation_id="scheduler_events_create",
    )
    def create_event(self, payload: EventIn):
        return 201, EventService.create(self.context.request.user, payload.model_dump())

    @http_patch(
        "/events/{event_uuid}/",
        response={200: EventOut, **MUTATION_ERROR_RESPONSES},
        operation_id="scheduler_events_update",
    )
    def update_event(self, event_uuid: UUID4, payload: EventPatchIn):
        instance = get_event(self.context.request, event_uuid)
        return EventService.update(instance, payload.model_dump(exclude_unset=True))

    @http_delete(
        "/events/{event_uuid}/",
        response={204: None, **MUTATION_ERROR_RESPONSES},
        operation_id="scheduler_events_delete",
    )
    def delete_event(self, event_uuid: UUID4):
        instance = get_event(self.context.request, event_uuid)
        EventService.delete(instance)
        return 204, None

    # --- TASKS ---

    @http_get("/tasks/", response=list[TaskOut], operation_id="scheduler_tasks_list")
    @paginate
    def list_tasks(self, wedding_id: UUID4 | None = None) -> QuerySet[Task]:
        return TaskService.list(self.context.request.user, wedding_id=wedding_id)

    @http_get(
        "/tasks/{task_uuid}/",
        response={200: TaskOut, **READ_ERROR_RESPONSES},
        operation_id="scheduler_tasks_read",
    )
    def get_task(self, task_uuid: UUID4):
        return get_task(self.context.request, task_uuid)

    @http_post(
        "/tasks/",
        response={201: TaskOut, **MUTATION_ERROR_RESPONSES},
        operation_id="scheduler_tasks_create",
    )
    def create_task(self, payload: TaskIn):
        return 201, TaskService.create(self.context.request.user, payload.model_dump())

    @http_patch(
        "/tasks/{task_uuid}/",
        response={200: TaskOut, **MUTATION_ERROR_RESPONSES},
        operation_id="scheduler_tasks_update",
    )
    def update_task(self, task_uuid: UUID4, payload: TaskPatchIn):
        instance = get_task(self.context.request, task_uuid)
        return TaskService.update(instance, payload.model_dump(exclude_unset=True))

    @http_delete(
        "/tasks/{task_uuid}/",
        response={204: None, **MUTATION_ERROR_RESPONSES},
        operation_id="scheduler_tasks_delete",
    )
    def delete_task(self, task_uuid: UUID4):
        instance = get_task(self.context.request, task_uuid)
        TaskService.delete(instance)
        return 204, None
