import logging
from datetime import datetime

from django.http import HttpRequest
from ninja import Router, Schema

from apps.core.cron import cron_registry
from apps.core.decorators import require_oidc_auth


logger = logging.getLogger(__name__)

cron_router = Router(tags=["Internal Cron"])


class BatchTaskResult(Schema):
    task: str
    status: str
    message: str
    executed_at: str


class DailyBatchResponse(Schema):
    status: str
    timestamp: datetime
    tasks: list[BatchTaskResult]


@cron_router.post(
    "/daily-batch/",
    response={200: DailyBatchResponse, 207: DailyBatchResponse},
    auth=None,
    operation_id="core_cron_daily_batch",
)
@require_oidc_auth
def run_daily_cron_batch(request: HttpRequest) -> tuple[int, DailyBatchResponse]:
    """
    Endpoint de disparo em lote (Daily Batch) para tarefas agendadas.
    Invocado pelo GCP Cloud Scheduler via POST seguro com OIDC (ADR-005).
    Executa todas as tarefas registradas no CronRegistry em uma única chamada On-Demand.

    Retorna HTTP 200 se todas as tarefas obtiverem sucesso.
    Retorna HTTP 207 (Multi-Status) se houver falha parcial ou total no lote,
    garantindo que o GCP Cloud Scheduler e alertas de monitoramento detectem o erro.
    """
    logger.info("Iniciando execução do lote diário de tarefas (Daily Batch Cron)...")

    # Executa todas as tarefas dinamicamente registradas no CronRegistry
    tasks_executed = cron_registry.run_batch()

    has_errors = any(t["status"] == "error" for t in tasks_executed)
    batch_status = "completed_with_errors" if has_errors else "completed"
    http_status = 207 if has_errors else 200

    if has_errors:
        logger.error("Lote diário finalizado com erros. Status HTTP: %d", http_status)

    payload = DailyBatchResponse(
        status=batch_status,
        timestamp=datetime.now(),
        tasks=[
            BatchTaskResult(
                task=t["task"],
                status=t["status"],
                message=t["message"],
                executed_at=t["executed_at"],
            )
            for t in tasks_executed
        ],
    )
    return http_status, payload
