"""
Serviço para gerenciamento de Notificações In-App.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import TYPE_CHECKING, cast
from uuid import UUID

from django.db import transaction

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

    Regras de Negócio e SSOT:
    - BR-N01..04 (Ciclo de Vida e Leitura de Notificações In-App):
      docs/architecture/business-rules/notifications/in-app-notifications-rules.md
    - Hub do Domínio de Notificações:
      docs/architecture/domains/notifications-domain.md
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
        wedding_name: str | None = None,
    ) -> Notification:
        """Cria e persiste uma nova notificação in-app no banco de dados.

        Regras de Negócio:
            BR-N01..04 (docs/architecture/business-rules/notifications/in-app-notifications-rules.md)

        Efeitos Colaterais:
            - Persiste a instância de Notification no banco de dados.
            - Resolve e associa o nome do casamento via weddings.interfaces se omitido.

        Args:
            notification_type: Tipo da notificação (NotificationType).
            link: URL ou rota de navegação opcional.
            target_type: Tipo da entidade ERP de destino (NotificationTargetType).
            target_id: Identificador do recurso de destino.
            wedding_id: Identificador do casamento relacionado.
            wedding_name: Nome pré-computado do casamento para exibição direta.

        Returns:
            A notificação criada e persistida.

        Raises:
            BusinessRuleViolation: Se o usuário não pertencer à empresa informada.
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

        if wedding_id and wedding_name is None:
            from apps.weddings.interfaces import get_wedding_display_name

            wedding_name = get_wedding_display_name(company, wedding_id)

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
            wedding_name=wedding_name,
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
        wedding_name: str | None = None,
    ) -> None:
        """Enfileira a criação assíncrona de uma notificação in-app via django.tasks.

        Efeitos Colaterais:
            - Enfileira a tarefa assíncrona dispatch_async_notification_task pós-chamada.

        Args:
            notification_type: Tipo da notificação (NotificationType).
            link: URL ou rota de navegação opcional.
            target_type: Tipo da entidade ERP de destino (NotificationTargetType).
            target_id: Identificador do recurso de destino.
            wedding_id: Identificador do casamento relacionado.
            wedding_name: Nome do casamento para exibição direta.
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
            wedding_name=wedding_name,
        )

    @staticmethod
    @transaction.atomic
    def mark_as_read(
        company: Company,
        user: User,
        notification_id: UUID | str,
    ) -> AnnotatedNotification:
        """Marca notificação como lida se ela pertencer ao usuário e empresa.

        Efeitos Colaterais:
            - Atualiza os campos is_read, read_at e updated_at no banco de dados.

        Args:
            notification_id: Identificador único da notificação.

        Returns:
            Instância da notificação marcada como lida com wedding_name anotado.

        Raises:
            ObjectNotFoundError: Se a notificação não existir ou pertencer a outro usuário/tenant.
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
            notification.mark_as_read()
            notification.save(update_fields=["is_read", "read_at", "updated_at"])
            logger.info(
                "Notificação marcada como lida: uuid=%s para user_id=%s",
                notification.uuid,
                user.id,
            )

        return cast(AnnotatedNotification, notification)

    @staticmethod
    @transaction.atomic
    def mark_all_as_read(company: Company, user: User) -> int:
        """Marca todas as notificações pendentes do usuário como lidas no tenant.

        Efeitos Colaterais:
            - Atualiza em lote os campos is_read, read_at e updated_at das notificações.

        Returns:
            Quantidade de notificações alteradas para o estado lida.
        """
        qs = Notification.objects.for_tenant(company).for_user(user)
        count = qs.mark_as_read()
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
        """Exclui uma notificação individual do usuário no tenant.

        Efeitos Colaterais:
            - Remove o registro da notificação do banco de dados.

        Args:
            notification_id: Identificador único da notificação.

        Raises:
            ObjectNotFoundError: Se a notificação não existir ou pertencer a outro usuário/tenant.
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

        Efeitos Colaterais:
            - Atualiza em lote os campos is_read, read_at e updated_at dos registros selecionados.

        Args:
            notification_ids: Sequência de identificadores das notificações a marcar como lidas.

        Returns:
            Quantidade de notificações atualizadas para o estado lida.
        """
        qs = (
            Notification.objects.for_tenant(company)
            .for_user(user)
            .filter(uuid__in=notification_ids)
        )
        count = qs.mark_as_read()
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
        """Exclui uma lista de notificações selecionadas no tenant.

        Efeitos Colaterais:
            - Remove em lote os registros de notificações selecionadas do banco de dados.

        Args:
            notification_ids: Sequência de identificadores das notificações a excluir.

        Returns:
            Quantidade de notificações excluídas.
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
        return int(count)

    @staticmethod
    @transaction.atomic
    def clear_all(company: Company, user: User) -> int:
        """Exclui todas as notificações do usuário no tenant atual.

        Efeitos Colaterais:
            - Remove todas as notificações do usuário no tenant do banco de dados.

        Returns:
            Quantidade total de notificações excluídas.
        """
        qs = Notification.objects.for_tenant(company).for_user(user)
        count, _ = qs.delete()
        logger.info(
            "Todas as notificações foram limpas: count=%d para user_id=%s",
            count,
            user.id,
        )
        return int(count)
