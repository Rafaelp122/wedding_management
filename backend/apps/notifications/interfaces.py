"""Interfaces públicas para o Bounded Context de Notificações (apps.notifications).

Seguindo a ADR-031, este arquivo expõe exclusivamente os contratos de despacho
e criação de notificações para outros domínios, preservando o encapsulamento interno
e garantindo execução em segundo plano pós-commit (transaction.on_commit).
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from django.db import transaction

from apps.notifications.tasks import dispatch_async_notification_task


if TYPE_CHECKING:
    from apps.notifications.models import Notification
    from apps.tenants.models import Company
    from apps.users.models import User


def notify_installment_overdue(
    *,
    company: Company,
    installment_uuid: UUID | str,
    expense_name: str,
    installment_number: int,
    amount: Decimal | str,
    due_date: date,
    wedding_uuid: UUID | str | None = None,
    wedding_name: str | None = None,
    users: Sequence[User],
) -> None:
    """Enfileira notificações de parcela vencida para os usuários do tenant.

    Registra o despacho assíncrono exclusivamente após a confirmação da transação
    (transaction.on_commit) para mitigar envio de notificações em caso de rollback.

    Args:
        company: Empresa (tenant) proprietária da parcela.
        installment_uuid: Identificador único da parcela ou despesa.
        expense_name: Nome descritivo da despesa vinculada.
        installment_number: Número ordinal da parcela.
        amount: Valor monetário da parcela.
        due_date: Data de vencimento da parcela.
        wedding_uuid: UUID opcional do casamento relacionado.
        wedding_name: Nome formatado opcional do casamento.
        users: Lista de usuários destinatários da notificação.
    """
    if not users:
        return

    company_id = company.id
    target_id_str = str(installment_uuid)
    wedding_id_str = str(wedding_uuid) if wedding_uuid else None
    resolved_wedding_name = wedding_name or ""
    formatted_date = due_date.strftime("%d/%m/%Y")
    link = f"/weddings/{wedding_uuid}?tab=finances" if wedding_uuid else "/weddings"
    message = (
        f"A parcela {installment_number} de '{expense_name}' "
        f"no valor de R$ {amount} venceu em {formatted_date}."
    )

    user_ids = [u.id for u in users if u.is_active]

    def _enqueue_notifications() -> None:
        for user_id in user_ids:
            dispatch_async_notification_task.enqueue(
                company_id=company_id,
                user_id=user_id,
                title="Parcela Vencida",
                message=message,
                notification_type="OVERDUE_INSTALLMENT",
                link=link,
                target_type="installment",
                target_id=target_id_str,
                wedding_id=wedding_id_str,
                wedding_name=resolved_wedding_name,
            )

    transaction.on_commit(_enqueue_notifications)


def send_notification_async(
    *,
    company_id: int | str,
    user_id: int | str,
    title: str,
    message: str,
    notification_type: str = "GENERAL",
    link: str = "",
    target_type: str = "",
    target_id: UUID | str | None = None,
    wedding_id: UUID | str | None = None,
    wedding_name: str = "",
) -> None:
    """Enfileira o envio assíncrono de notificação genérica pós-commit.

    Args:
        company_id: ID ou UUID da empresa tenant.
        user_id: ID ou UUID do usuário destinatário.
        title: Título da notificação.
        message: Conteúdo detalhado.
        notification_type: Tipo da notificação (ex: GENERAL, REMINDER).
        link: Link de redirecionamento opcional.
        target_type: Tipo do recurso vinculado.
        target_id: Identificador do recurso vinculado.
        wedding_id: Identificador do casamento relacionado.
        wedding_name: Nome do casamento relacionado.
    """
    target_id_str = str(target_id) if target_id else None
    wedding_id_str = str(wedding_id) if wedding_id else None

    def _enqueue() -> None:
        dispatch_async_notification_task.enqueue(
            company_id=company_id,
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            link=link,
            target_type=target_type,
            target_id=target_id_str,
            wedding_id=wedding_id_str,
            wedding_name=wedding_name,
        )

    transaction.on_commit(_enqueue)


def create_notification(
    *,
    company: Company | UUID | str | int,
    user: User | UUID | str | int,
    title: str,
    message: str,
    notification_type: str = "GENERAL",
    link: str = "",
    target_type: str = "",
    target_id: UUID | str | None = None,
    wedding_id: UUID | str | None = None,
    wedding_name: str | None = None,
) -> Notification:
    """Cria e persiste uma notificação diretamente no domínio de notificações.

    Args:
        company: Empresa (tenant) proprietária.
        user: Usuário destinatário.
        title: Título da notificação.
        message: Mensagem textual detalhada.
        notification_type: Tipo da notificação.
        link: URL ou rota associada.
        target_type: Tipo do recurso ERP.
        target_id: Identificador do recurso.
        wedding_id: UUID do casamento.
        wedding_name: Nome do casamento.

    Returns:
        Notification: A notificação persistida.
    """
    from apps.notifications.services import NotificationService

    return NotificationService.create_notification(
        company=company,
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        link=link,
        target_type=target_type,
        target_id=target_id,
        wedding_id=wedding_id,
        wedding_name=wedding_name,
    )
