"""
Serviço para gerenciamento de Notificações In-App.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import TYPE_CHECKING, cast
from uuid import UUID

from django.db import transaction
from django.utils import timezone

from apps.core.exceptions import BusinessRuleViolation, ObjectNotFoundError
from apps.notifications.models import Notification, NotificationType
from apps.notifications.tasks import dispatch_async_notification_task
from apps.tenants.models import Company
from apps.users.models import User


logger = logging.getLogger(__name__)


if TYPE_CHECKING:

    class AnnotatedNotification(Notification):
        """Notificação com o nome do casamento calculado pela consulta."""

        wedding_name: str | None

else:
    AnnotatedNotification = Notification


class NotificationService:
    """Serviço para gerenciamento de Notificações In-App.

    Centraliza a criação e alteração do estado de notificações (mutações),
    garantindo isolamento multitenant.
    """

    @staticmethod
    @transaction.atomic
    def create_notification(
        company: Company | UUID | str | int,
        user: User | UUID | str | int,
        title: str,
        message: str,
        notification_type: str = NotificationType.GENERAL,
        link: str = "",
        target_type: str = "",
        target_id: UUID | str | None = None,
        wedding_id: UUID | str | None = None,
    ) -> Notification:
        """Cria e persiste uma nova notificação no banco de dados.

        Args:
            company: Instância da empresa ou identificador (ID/UUID).
            user: Instância do usuário ou identificador (ID/UUID).
            title: Título resumido da notificação.
            message: Conteúdo textual detalhado da notificação.
            notification_type: Tipo da notificação (NotificationType).
            link: URL ou rota de atalho opcional.
            target_type: Tipo da entidade ERP de destino.
            target_id: UUID do recurso de destino.
            wedding_id: UUID do casamento associado.

        Returns:
            Notification: A notificação criada.
        """
        if not isinstance(company, Company):
            company = (
                Company.objects.get(pk=company)
                if isinstance(company, int)
                else Company.objects.get(uuid=company)
            )
        if not isinstance(user, User):
            user = (
                User.objects.get(pk=user)
                if isinstance(user, int)
                else User.objects.get(uuid=user)
            )

        if user.company_id != company.id:
            raise BusinessRuleViolation("Usuário não pertence à empresa informada.")

        notification = Notification(
            company=company,
            user=user,
            title=title,
            message=message,
            type=notification_type,
            link=link,
            target_type=target_type,
            target_id=target_id,
            wedding_id=wedding_id,
            is_read=False,
        )
        notification.save()
        logger.info(
            "Notificação criada com sucesso: uuid=%s para user_id=%s",
            notification.uuid,
            user.id,
        )
        return notification

    @staticmethod
    @transaction.atomic
    def notify(
        company: Company | UUID | str | int,
        user: User | UUID | str | int,
        title: str,
        message: str,
        notification_type: str = NotificationType.GENERAL,
        link: str = "",
        target_type: str = "",
        target_id: UUID | str | None = None,
        wedding_id: UUID | str | None = None,
    ) -> Notification:
        """
        Atalho de conveniência para criação e envio de notificação.

        Args:
            company: Instância ou identificador da empresa (tenant).
            user: Usuário destinatário da notificação.
            title: Título da notificação.
            message: Mensagem textual da notificação.
            notification_type: Tipo da notificação (ex: GENERAL, REMINDER).
            link: URL ou rota associada.
            target_type: Tipo do recurso vinculado.
            target_id: Identificador do recurso vinculado.
            wedding_id: Identificador do casamento relacionado.

        Returns:
            A notificação criada e persistida.
        """
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
        )

    @staticmethod
    def create_async_notification(
        company: Company | UUID | str | int,
        user: User | UUID | str | int,
        title: str,
        message: str,
        notification_type: str = NotificationType.GENERAL,
        link: str = "",
        target_type: str = "",
        target_id: UUID | str | None = None,
        wedding_id: UUID | str | None = None,
    ) -> None:
        """Enfileira a criação assíncrona de uma notificação in-app via django.tasks.

        Args:
            company: Instância da empresa ou identificador.
            user: Instância do usuário ou identificador.
            title: Título da notificação.
            message: Conteúdo detalhado.
            notification_type: Tipo da notificação.
            link: Link opcional.
            target_type: Tipo da entidade ERP de destino.
            target_id: UUID do recurso de destino.
            wedding_id: UUID do casamento associado.
        """
        company_id: int | str = (
            company.id
            if isinstance(company, Company)
            else (company if isinstance(company, int) else str(company))
        )
        user_id: int | str = (
            user.id
            if isinstance(user, User)
            else (user if isinstance(user, int) else str(user))
        )

        dispatch_async_notification_task.enqueue(
            company_id=company_id,
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            link=link,
            target_type=target_type,
            target_id=str(target_id) if target_id else None,
            wedding_id=str(wedding_id) if wedding_id else None,
        )

    @staticmethod
    @transaction.atomic
    def mark_as_read(
        company: Company,
        user: User,
        notification_id: UUID | str,
    ) -> AnnotatedNotification:
        """Marca notificação como lida se ela pertencer ao usuário e empresa.

        Args:
            company: O tenant atual para isolamento multitenancy.
            user: O usuário autenticado solicitante.
            notification_id: UUID público da notificação.

        Returns:
            Notification: Notificação atualizada.

        Raises:
            ObjectNotFoundError: Se a notificação não existir ou pertencer a outro
                usuário/tenant.
        """
        notification = (
            Notification.objects.for_tenant(company)
            .for_user(user)
            .with_wedding_name()
            .filter(uuid=notification_id)
            .first()
        )
        if not notification:
            raise ObjectNotFoundError(detail="Notificação não encontrada.")

        if not notification.is_read:
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save()
            logger.info(
                "Notificação marcada como lida: uuid=%s para user_id=%s",
                notification.uuid,
                user.id,
            )

        return cast(AnnotatedNotification, notification)

    @staticmethod
    @transaction.atomic
    def mark_all_as_read(company: Company, user: User) -> int:
        """Marca todas as notificações pendentes do usuário como lidas.

        Args:
            company: O tenant atual para isolamento multitenancy.
            user: O usuário cujas notificações serão atualizadas.

        Returns:
            int: Quantidade de notificações que mudaram para lidas.
        """
        now = timezone.now()
        qs = Notification.objects.for_tenant(company).for_user(user).unread()
        count = qs.update(is_read=True, read_at=now, updated_at=now)
        logger.info(
            "Todas as notificações marcadas como lidas: count=%d para user_id=%s",
            count,
            user.id,
        )
        return count

    @staticmethod
    @transaction.atomic
    def delete_notification(
        company: Company,
        user: User,
        notification_id: UUID | str,
    ) -> None:
        """Exclui uma notificação individual do usuário.

        Args:
            company: O tenant atual para isolamento multitenancy.
            user: O usuário autenticado solicitante.
            notification_id: UUID público da notificação.

        Raises:
            ObjectNotFoundError: Se a notificação não existir ou pertencer
                a outro usuário.
        """
        notification = (
            Notification.objects.for_tenant(company)
            .for_user(user)
            .filter(uuid=notification_id)
            .first()
        )
        if not notification:
            raise ObjectNotFoundError(detail="Notificação não encontrada.")

        notification.delete()
        logger.info(
            "Notificação excluída com sucesso: uuid=%s para user_id=%s",
            notification_id,
            user.id,
        )

    @staticmethod
    @transaction.atomic
    def bulk_mark_as_read(
        company: Company,
        user: User,
        notification_ids: Sequence[UUID | str],
    ) -> int:
        """Marca uma lista de notificações selecionadas como lidas.

        Args:
            company: O tenant atual para isolamento multitenancy.
            user: O usuário cujas notificações serão atualizadas.
            notification_ids: Sequência de UUIDs das notificações.

        Returns:
            int: Quantidade de notificações atualizadas.
        """
        now = timezone.now()
        qs = (
            Notification.objects.for_tenant(company)
            .for_user(user)
            .unread()
            .filter(uuid__in=notification_ids)
        )
        count = qs.update(is_read=True, read_at=now, updated_at=now)
        logger.info(
            "Notificações em lote marcadas como lidas: count=%d para user_id=%s",
            count,
            user.id,
        )
        return count

    @staticmethod
    @transaction.atomic
    def bulk_delete(
        company: Company,
        user: User,
        notification_ids: Sequence[UUID | str],
    ) -> int:
        """Exclui uma lista de notificações selecionadas.

        Args:
            company: O tenant atual para isolamento multitenancy.
            user: O usuário cujas notificações serão excluídas.
            notification_ids: Sequência de UUIDs das notificações.

        Returns:
            int: Quantidade de notificações excluídas.
        """
        qs = (
            Notification.objects.for_tenant(company)
            .for_user(user)
            .filter(uuid__in=notification_ids)
        )
        count, _ = qs.delete()
        logger.info(
            "Notificações em lote excluídas: count=%d para user_id=%s",
            count,
            user.id,
        )
        return count

    @staticmethod
    @transaction.atomic
    def clear_all(company: Company, user: User) -> int:
        """Exclui todas as notificações do usuário no tenant atual.

        Args:
            company: O tenant atual para isolamento multitenancy.
            user: O usuário cujas notificações serão limpas.

        Returns:
            int: Quantidade total de notificações excluídas.
        """
        qs = Notification.objects.for_tenant(company).for_user(user)
        count, _ = qs.delete()
        logger.info(
            "Todas as notificações foram limpas: count=%d para user_id=%s",
            count,
            user.id,
        )
        return count
