import logging
from collections.abc import Sequence
from uuid import UUID

from django.db import transaction
from django.db.models import OuterRef, QuerySet, Subquery, Value
from django.db.models.functions import Concat
from django.utils import timezone

from apps.core.exceptions import BusinessRuleViolation, ObjectNotFoundError
from apps.notifications.models import Notification, NotificationType
from apps.notifications.tasks import dispatch_async_notification_task
from apps.tenants.models import Company
from apps.users.models import User


logger = logging.getLogger(__name__)


def _get_wedding_name_subquery() -> Subquery:
    """Retorna uma subquery anotando o nome formatado do casamento."""
    from apps.weddings.models import Wedding

    return Subquery(
        Wedding.objects.filter(uuid=OuterRef("wedding_id")).values(
            name=Concat(
                Value("Casamento de "),
                "bride_name",
                Value(" e "),
                "groom_name",
            )
        )[:1]
    )


class NotificationService:
    """Serviço para gerenciamento de Notificações In-App.

    Centraliza a criação, listagem e alteração do estado de notificações,
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
    def list_notifications(
        company: Company,
        user: User,
        is_read: bool | None = None,
    ) -> QuerySet[Notification]:
        """Lista todas as notificações de um usuário vinculadas à sua empresa.

        Args:
            company: O tenant atual para isolamento multitenancy.
            user: O usuário destinatário das notificações.
            is_read: Filtro opcional por estado de leitura.

        Returns:
            QuerySet[Notification]: Notificações filtradas do usuário com
                wedding_name anotado em SQL.
        """
        qs = (
            Notification.objects.for_tenant(company)
            .filter(user=user)
            .annotate(wedding_name=_get_wedding_name_subquery())
        )
        if is_read is not None:
            qs = qs.filter(is_read=is_read)

        return qs

    @staticmethod
    def get_unread_count(company: Company, user: User) -> int:
        """Obtém a contagem de notificações não lidas de um usuário.

        Args:
            company: O tenant atual para isolamento multitenancy.
            user: O usuário alvo da contagem.

        Returns:
            int: Quantidade de notificações com is_read=False.
        """
        return (
            Notification.objects.for_tenant(company)
            .filter(user=user, is_read=False)
            .count()
        )

    @staticmethod
    @transaction.atomic
    def mark_as_read(
        company: Company,
        user: User,
        notification_id: UUID | str,
    ) -> Notification:
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
            .annotate(wedding_name=_get_wedding_name_subquery())
            .filter(uuid=notification_id, user=user)
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

        return notification

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
        qs = Notification.objects.for_tenant(company).filter(user=user, is_read=False)
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
            .filter(uuid=notification_id, user=user)
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
        qs = Notification.objects.for_tenant(company).filter(
            user=user, uuid__in=notification_ids, is_read=False
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
        qs = Notification.objects.for_tenant(company).filter(
            user=user, uuid__in=notification_ids
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
        qs = Notification.objects.for_tenant(company).filter(user=user)
        count, _ = qs.delete()
        logger.info(
            "Todas as notificações foram limpas: count=%d para user_id=%s",
            count,
            user.id,
        )
        return count
