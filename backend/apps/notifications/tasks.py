from django.tasks import task


@task()
def dispatch_async_notification_task(
    company_id: int | str,
    user_id: int | str,
    title: str,
    message: str,
    notification_type: str = "GENERAL",
    link: str = "",
    target_type: str = "",
    target_id: str | None = None,
    wedding_id: str | None = None,
) -> None:
    """Tarefa assíncrona para despacho de notificações in-app.

    Args:
        company_id: ID ou UUID da empresa tenant.
        user_id: ID ou UUID do usuário destinatário.
        title: Título da notificação.
        message: Conteúdo detalhado da notificação.
        notification_type: Tipo da notificação (NotificationType).
        link: Link de redirecionamento opcional.
        target_type: Tipo da entidade ERP de destino.
        target_id: UUID do recurso de destino.
        wedding_id: UUID do casamento associado.
    """
    from apps.notifications.services import NotificationService
    from apps.tenants.models import Company
    from apps.users.models import User

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

    NotificationService.create_notification(
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
