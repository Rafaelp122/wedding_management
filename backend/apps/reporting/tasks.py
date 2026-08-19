"""
Tarefas assíncronas em segundo plano do app reporting (django.tasks).
"""

import logging
from typing import Literal

from django.tasks import task


logger = logging.getLogger(__name__)


@task()
def generate_wedding_report_task(
    company_id: int | str,
    user_id: int | str,
    wedding_id: str,
    report_format: str = "pdf",
) -> None:
    """
    Tarefa assíncrona para geração e armazenamento de relatório de casamento.

    Gera o arquivo binário em segundo plano, persiste no Cloudflare R2 / S3
    e despacha uma notificação in-app com o link de download para o usuário.

    Args:
        company_id: ID ou UUID da empresa tenant.
        user_id: ID ou UUID do usuário solicitante.
        wedding_id: UUID do casamento a ser exportado.
        report_format: Formato do relatório ('pdf' ou 'excel').
    """
    logger.info(
        "Iniciando geração assíncrona de relatório (%s) para casamento uuid=%s",
        report_format,
        wedding_id,
    )

    from apps.notifications.services import NotificationService
    from apps.reporting.services import ReportGenerationService
    from apps.tenants.models import Company
    from apps.users.models import User
    from apps.weddings.models import Wedding

    company = (
        Company.objects.get(pk=company_id)
        if isinstance(company_id, int)
        else Company.objects.get(uuid=company_id)
    )
    user = (
        User.objects.get(pk=user_id)
        if isinstance(user_id, int)
        else User.objects.get(uuid=user_id)
    )
    wedding = Wedding.objects.for_tenant(company).get(uuid=wedding_id)

    fmt: Literal["pdf", "excel"] = (
        "excel" if report_format.lower() == "excel" else "pdf"
    )
    _, download_url = ReportGenerationService.generate_and_store_report(
        company=company,
        wedding_uuid=wedding.uuid,
        report_format=fmt,
    )

    format_label = "Excel" if fmt == "excel" else "PDF"
    couple_name = f"{wedding.groom_name} & {wedding.bride_name}"
    msg = (
        f"O relatório em {format_label} do casamento {couple_name} "
        "foi gerado com sucesso."
    )

    NotificationService.create_notification(
        company=company,
        user=user,
        title="Relatório Pronto para Download",
        message=msg,
        notification_type="GENERAL",
        link=download_url,
        target_type="wedding",
        target_id=str(wedding.uuid),
        wedding_id=str(wedding.uuid),
    )

    logger.info(
        "Relatório assíncrono (%s) concluído com sucesso para casamento uuid=%s",
        report_format,
        wedding_id,
    )
