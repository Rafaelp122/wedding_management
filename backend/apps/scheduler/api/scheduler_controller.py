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

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.scheduler.dependencies import get_appointment, get_task
from apps.scheduler.models import Appointment, Task
from apps.scheduler.schemas import (
    AppointmentIn,
    AppointmentOut,
    AppointmentPatchIn,
    TaskIn,
    TaskOut,
    TaskPatchIn,
)
from apps.scheduler.services.appointments import AppointmentService
from apps.scheduler.services.tasks import TaskService


@api_controller("/scheduler", tags=["Scheduler"])
class SchedulerController(ControllerBase):
    """
    Controlador para Gestão de Agenda e Tarefas (RF07 / RF08).
    """

    # --- APPOINTMENTS (RF07) ---

    @http_get(
        "/appointments/",
        response={200: list[AppointmentOut], **READ_ERROR_RESPONSES},
        operation_id="scheduler_appointments_list",
    )
    @paginate
    def list_appointments(self, event_id: UUID4 | None = None) -> QuerySet[Appointment]:
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        assert self.context.request.user  # noqa: S101
        return AppointmentService.list(self.context.request.user, event_id)

    @http_get(
        "/appointments/{appointment_uuid}/",
        response={200: AppointmentOut, **READ_ERROR_RESPONSES},
        operation_id="scheduler_appointments_retrieve",
    )
    def retrieve_appointment(self, appointment_uuid: UUID4):
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        return get_appointment(self.context.request, appointment_uuid)

    @http_post(
        "/appointments/",
        response={201: AppointmentOut, **MUTATION_ERROR_RESPONSES},
        operation_id="scheduler_appointments_create",
    )
    def create_appointment(self, payload: AppointmentIn):
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        assert self.context.request.user  # noqa: S101
        return 201, AppointmentService.create(
            self.context.request.user, payload.model_dump()
        )

    @http_patch(
        "/appointments/{appointment_uuid}/",
        response={200: AppointmentOut, **MUTATION_ERROR_RESPONSES},
        operation_id="scheduler_appointments_update",
    )
    def update_appointment(self, appointment_uuid: UUID4, payload: AppointmentPatchIn):
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        instance = get_appointment(self.context.request, appointment_uuid)
        return AppointmentService.update(
            instance, payload.model_dump(exclude_unset=True)
        )

    @http_delete(
        "/appointments/{appointment_uuid}/",
        response={204: None, **MUTATION_ERROR_RESPONSES},
        operation_id="scheduler_appointments_delete",
    )
    def delete_appointment(self, appointment_uuid: UUID4):
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        instance = get_appointment(self.context.request, appointment_uuid)
        AppointmentService.delete(instance)
        return 204, None

    # --- TASKS (RF08) ---

    @http_get(
        "/tasks/",
        response={200: list[TaskOut], **READ_ERROR_RESPONSES},
        operation_id="scheduler_tasks_list",
    )
    @paginate
    def list_tasks(self, event_id: UUID4 | None = None) -> QuerySet[Task]:
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        assert self.context.request.user  # noqa: S101
        return TaskService.list(self.context.request.user, event_id)

    @http_get(
        "/tasks/{task_uuid}/",
        response={200: TaskOut, **READ_ERROR_RESPONSES},
        operation_id="scheduler_tasks_retrieve",
    )
    def retrieve_task(self, task_uuid: UUID4):
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        return get_task(self.context.request, task_uuid)

    @http_post(
        "/tasks/",
        response={201: TaskOut, **MUTATION_ERROR_RESPONSES},
        operation_id="scheduler_tasks_create",
    )
    def create_task(self, payload: TaskIn):
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        assert self.context.request.user  # noqa: S101
        return 201, TaskService.create(self.context.request.user, payload.model_dump())

    @http_patch(
        "/tasks/{task_uuid}/",
        response={200: TaskOut, **MUTATION_ERROR_RESPONSES},
        operation_id="scheduler_tasks_update",
    )
    def update_task(self, task_uuid: UUID4, payload: TaskPatchIn):
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        instance = get_task(self.context.request, task_uuid)
        return TaskService.update(instance, payload.model_dump(exclude_unset=True))

    @http_delete(
        "/tasks/{task_uuid}/",
        response={204: None, **MUTATION_ERROR_RESPONSES},
        operation_id="scheduler_tasks_delete",
    )
    def delete_task(self, task_uuid: UUID4):
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        instance = get_task(self.context.request, task_uuid)
        TaskService.delete(instance)
        return 204, None
