from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel
from apps.tenants.managers import TenantManager
from apps.tenants.models import Company


class NotificationType(models.TextChoices):
    OVERDUE_INSTALLMENT = "OVERDUE_INSTALLMENT", _("Parcela Vencida")
    UPCOMING_INSTALLMENT = "UPCOMING_INSTALLMENT", _("Parcela a Vencer")
    EXPIRING_CONTRACT = "EXPIRING_CONTRACT", _("Contrato Prestes a Vencer")
    TASK_DEADLINE = "TASK_DEADLINE", _("Prazo de Tarefa")
    CHECKLIST_ITEM_OVERDUE = "CHECKLIST_ITEM_OVERDUE", _("Item de Checklist Vencido")
    GENERAL = "GENERAL", _("Geral")


class NotificationTargetType(models.TextChoices):
    INSTALLMENT = "installment", _("Parcela")
    EXPENSE = "expense", _("Despesa")
    TASK = "task", _("Tarefa")
    CONTRACT = "contract", _("Contrato")
    WEDDING = "wedding", _("Casamento")
    GENERAL = "general", _("Geral")


class Notification(BaseModel):
    """Modelo de Notificação In-App vinculada ao tenant e usuário."""

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("Empresa"),
    )
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("Usuário"),
    )
    title = models.CharField(_("Título"), max_length=255)
    message = models.TextField(_("Mensagem"))
    type = models.CharField(
        _("Tipo"),
        max_length=50,
        choices=NotificationType.choices,
        default=NotificationType.GENERAL,
    )
    target_type = models.CharField(
        _("Tipo de Alvo"),
        max_length=50,
        choices=NotificationTargetType.choices,
        blank=True,
        default="",
    )
    target_id = models.UUIDField(_("ID do Alvo"), null=True, blank=True, db_index=True)
    wedding_id = models.UUIDField(
        _("ID do Casamento"), null=True, blank=True, db_index=True
    )
    is_read = models.BooleanField(_("Lida"), default=False, db_index=True)
    link = models.CharField(_("Link"), max_length=500, blank=True, default="")
    read_at = models.DateTimeField(_("Lida em"), null=True, blank=True)

    objects = TenantManager()

    class Meta:
        verbose_name = _("Notificação")
        verbose_name_plural = _("Notificações")
        ordering = ["-created_at"]
        db_table = "notifications"
        indexes = [
            models.Index(fields=["company", "user", "is_read"]),
        ]

    def __str__(self) -> str:
        return f"[{self.type}] {self.title} ({self.user})"
