from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel
from apps.notifications.managers import NotificationQuerySet
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
    wedding_name = models.CharField(  # noqa: DJ001
        _("Nome do Casamento"), max_length=255, null=True, blank=True, default=None
    )
    is_read = models.BooleanField(_("Lida"), default=False, db_index=True)
    link = models.CharField(_("Link"), max_length=500, blank=True, default="")
    read_at = models.DateTimeField(_("Lida em"), null=True, blank=True)

    objects = NotificationQuerySet.as_manager()

    class Meta:
        verbose_name = _("Notificação")
        verbose_name_plural = _("Notificações")
        ordering = ["-created_at"]
        db_table = "notifications"
        indexes = [
            models.Index(fields=["company", "user", "is_read"]),
        ]

    def __str__(self) -> str:
        return f"[{self.type}] {self.title} (user_id={self.user_id})"

    def clean(self) -> None:
        """Valida o isolamento de tenant do usuário e sincroniza data de leitura."""
        super().clean()
        if self.user_id and self.company_id and self.user.company_id != self.company_id:
            raise ValidationError(
                {"user": "O usuário destinatário deve pertencer à empresa informada."}
            )
        if self.is_read and not self.read_at:
            self.read_at = timezone.now()
        elif not self.is_read and self.read_at is not None:
            self.read_at = None

    # ── Métodos Semânticos de Ciclo de Vida ──────────────────────────────

    def mark_as_read(self, read_at: datetime | None = None) -> None:
        """Marca a notificação como lida de forma idempotente.

        Args:
            read_at: Data/hora opcional da leitura. Se omitido, usa timezone.now().
        """
        if self.is_read:
            return
        self.is_read = True
        self.read_at = read_at or timezone.now()
