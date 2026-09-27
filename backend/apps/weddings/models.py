from __future__ import annotations

import datetime as dt
import sys
from datetime import date
from typing import Any, ClassVar

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.core.exceptions import BusinessRuleViolation
from apps.core.mixins import WeddingOwnedMixin
from apps.tenants.models import TenantModel
from apps.weddings.managers import WeddingQuerySet


def validate_future_date(value: date) -> None:
    """Validador auxiliar mantido para compatibilidade com migration 0001."""
    if value < timezone.now().date():
        raise ValidationError("A data do casamento não pode ser no passado.")


class Wedding(TenantModel):
    """
    Agregado central que representa um evento de casamento no sistema.

    Encapsula o ciclo de vida do planejamento, máquina de estados de transição,
    invariantes de data, dados do contratante e template de cronograma.
    """

    objects = WeddingQuerySet.as_manager()  # type: ignore[assignment,misc]

    class StatusChoices(models.TextChoices):
        PROPOSAL = "PROPOSAL", "Proposta"
        PLANNING = "PLANNING", "Planejamento"
        IN_PROGRESS = "IN_PROGRESS", "Em Andamento"
        COMPLETED = "COMPLETED", "Concluído"
        CANCELED = "CANCELED", "Cancelado"

    ALLOWED_TRANSITIONS: ClassVar[dict[str, list[str]]] = {
        StatusChoices.PROPOSAL.value: [
            StatusChoices.PLANNING.value,
            StatusChoices.IN_PROGRESS.value,
            StatusChoices.CANCELED.value,
        ],
        StatusChoices.PLANNING.value: [
            StatusChoices.IN_PROGRESS.value,
            StatusChoices.COMPLETED.value,
            StatusChoices.CANCELED.value,
        ],
        StatusChoices.IN_PROGRESS.value: [
            StatusChoices.COMPLETED.value,
            StatusChoices.CANCELED.value,
        ],
        StatusChoices.CANCELED.value: [
            StatusChoices.PLANNING.value,
            StatusChoices.IN_PROGRESS.value,
            StatusChoices.PROPOSAL.value,
        ],
        StatusChoices.COMPLETED.value: [],
    }

    groom_name = models.CharField(max_length=100)
    bride_name = models.CharField(max_length=100)
    date = models.DateField()
    location = models.CharField(max_length=255)
    expected_guests = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Número de Convidados",
        help_text="Quantidade estimada de convidados",
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.IN_PROGRESS,
    )
    template = models.CharField(  # noqa: DJ001
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Modelo de Cronograma",
        help_text="Template aplicado na criação do casamento",
    )

    # ── Dados do Contratante Principal (Responsável Financeiro) ───────────
    client_name = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Nome do Contratante",
    )
    client_cpf = models.CharField(
        max_length=14,
        blank=True,
        default="",
        verbose_name="CPF do Contratante",
    )
    client_email = models.EmailField(
        blank=True,
        default="",
        verbose_name="E-mail do Contratante",
    )
    client_phone = models.CharField(
        max_length=20,
        blank=True,
        default="",
        verbose_name="Telefone do Contratante",
    )
    client_role = models.CharField(
        max_length=50,
        blank=True,
        default="NOIVO",
        verbose_name="Papel do Contratante",
    )
    days_before_in_progress = models.PositiveIntegerField(
        default=7,
        verbose_name="Dias para Reta Final",
    )

    class Meta:
        verbose_name = "Casamento"
        verbose_name_plural = "Casamentos"
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["company", "status"]),
            models.Index(fields=["date"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"{self.groom_name} & {self.bride_name}"

    # ── Regras de Domínio e Invariantes (Nível 2) ─────────────────────────

    def clean(self) -> None:
        """Valida invariantes de integridade e consistência direta do modelo."""
        super().clean()
        today = timezone.now().date()
        if (
            self.status == self.StatusChoices.IN_PROGRESS
            and self.date
            and self.date < today
        ):
            if self._state.adding:
                raise ValidationError(
                    {"date": "A data do casamento não pode ser no passado."}
                )
            elif self.pk:
                orig = (
                    Wedding.objects.filter(pk=self.pk).values("date", "status").first()
                )
                if orig and (
                    orig["date"] != self.date or orig["status"] != self.status
                ):
                    raise ValidationError(
                        {"date": "A nova data do casamento não pode ser no passado."}
                    )

        if (
            self.status == self.StatusChoices.COMPLETED
            and self.date
            and self.date > today
        ):
            raise ValidationError(
                "Não pode marcar como CONCLUÍDO antes da data do casamento"
            )

        if self.pk:
            orig_status = Wedding.objects.filter(pk=self.pk).values("status").first()
            if orig_status and orig_status["status"] != self.status:
                allowed = self.ALLOWED_TRANSITIONS.get(orig_status["status"], [])
                if self.status not in allowed:
                    raise ValidationError(
                        f"Não é permitido transitar de "
                        f"'{orig_status['status']}' para '{self.status}'."
                    )

    # ── Métodos de Ciclo de Vida e Operações de Domínio ─────────────────

    def reschedule(self, new_date: dt.date) -> None:
        """
        Reagenda a data do casamento validando as regras temporais.

        Args:
            new_date: Nova data pretendida para a realização da cerimônia.

        Raises:
            BusinessRuleViolation: Se o casamento já estiver concluído ou a data
                for no passado.
        """
        if self.is_completed:
            raise BusinessRuleViolation(
                detail="Não é possível reagendar um casamento já concluído.",
                code="wedding_already_completed",
            )
        if new_date < timezone.now().date():
            raise BusinessRuleViolation(
                detail="A nova data do casamento não pode ser no passado.",
                code="wedding_reschedule_in_past",
            )
        self.date = new_date

    def update_details(
        self,
        *,
        groom_name: str | None = None,
        bride_name: str | None = None,
        location: str | None = None,
        expected_guests: int | object | None = ...,
        client_name: str | None = None,
        client_cpf: str | None = None,
        client_email: str | None = None,
        client_phone: str | None = None,
        client_role: str | None = None,
        days_before_in_progress: int | None = None,
    ) -> None:
        """
        Atualiza dados cadastrais descritivos e do contratante do casamento.

        Args:
            groom_name: Nome do noivo.
            bride_name: Nome da noiva.
            location: Local planejado para a realização.
            expected_guests: Quantidade estimada de convidados.
            client_name: Nome do contratante principal.
            client_cpf: CPF do contratante principal.
            client_email: E-mail do contratante principal.
            client_phone: Telefone do contratante principal.
            client_role: Papel ou parentesco do contratante principal.
            days_before_in_progress: Dias de antecedência para disparo da reta final.
        """
        if groom_name is not None:
            self.groom_name = groom_name
        if bride_name is not None:
            self.bride_name = bride_name
        if location is not None:
            self.location = location
        if expected_guests is not ...:
            self.expected_guests = expected_guests  # type: ignore[assignment]
        if client_name is not None:
            self.client_name = client_name
        if client_cpf is not None:
            self.client_cpf = client_cpf
        if client_email is not None:
            self.client_email = client_email
        if client_phone is not None:
            self.client_phone = client_phone
        if client_role is not None:
            self.client_role = client_role
        if days_before_in_progress is not None:
            self.days_before_in_progress = days_before_in_progress

    def can_transition_to(self, target_status: str | StatusChoices) -> bool:
        """Verifica se a transição para o status informado é válida."""
        target = str(target_status)
        if self.status == target:
            return True
        allowed = self.ALLOWED_TRANSITIONS.get(self.status, [])
        if target not in allowed:
            return False
        if target == self.StatusChoices.COMPLETED and self.date > timezone.now().date():
            return False
        if (
            target in (self.StatusChoices.IN_PROGRESS, self.StatusChoices.PLANNING)
            and self.date
            and self.date < timezone.now().date()
        ):
            return False
        return True

    def transition_to(self, target_status: str | StatusChoices) -> None:
        """
        Executa a transição de status validando as regras de negócio de domínio.

        Raises:
            BusinessRuleViolation: Se a transição for proibida ou prematura.
        """
        target = str(target_status)
        if self.status == target:
            return

        if not self.can_transition_to(target):
            if (
                target == self.StatusChoices.COMPLETED
                and self.date > timezone.now().date()
            ):
                raise BusinessRuleViolation(
                    detail="Não pode marcar como CONCLUÍDO antes da data do casamento",
                    code="wedding_premature_completion",
                )
            if (
                target in (self.StatusChoices.IN_PROGRESS, self.StatusChoices.PLANNING)
                and self.date
                and self.date < timezone.now().date()
            ):
                raise BusinessRuleViolation(
                    detail="A data do casamento não pode ser no passado para iniciar o planejamento.",
                    code="wedding_date_in_past",
                )
            raise BusinessRuleViolation(
                detail=f"Não é permitido transitar de '{self.status}' para '{target}'.",
                code="wedding_invalid_status_transition",
            )

        self.status = self.StatusChoices(target)

    def convert_to_planning(self) -> None:
        """
        Transiciona o casamento de PROPOSTA para PLANEJAMENTO (PLANNING).

        Valida que o evento possa transitar para planejamento e que a data
        da cerimônia não seja retroativa.

        Raises:
            BusinessRuleViolation: Se o status atual for incompatível ou a data for no passado.
        """
        if self.status not in (
            self.StatusChoices.PROPOSAL,
            self.StatusChoices.PLANNING,
        ):
            raise BusinessRuleViolation(
                detail=f"Não é permitido transitar de '{self.status}' para '{self.StatusChoices.PLANNING}'.",
                code="wedding_invalid_status_transition",
            )
        if self.date and self.date < timezone.now().date():
            raise BusinessRuleViolation(
                detail="A data do casamento não pode ser no passado para iniciar o planejamento.",
                code="wedding_date_in_past",
            )
        self.transition_to(self.StatusChoices.PLANNING)

    def complete(self) -> None:
        """Conclui o casamento garantindo que o evento já foi realizado."""
        self.transition_to(self.StatusChoices.COMPLETED)

    def cancel(self) -> None:
        """Cancela o casamento."""
        self.transition_to(self.StatusChoices.CANCELED)

    def reopen(self) -> None:
        """Reabre um casamento previamente cancelado voltando para EM ANDAMENTO."""
        self.transition_to(self.StatusChoices.IN_PROGRESS)

    # ── Propriedades e Métodos de Domínio ────────────────────────────────

    @property
    def display_name(self) -> str:
        """Retorna o nome formatado de exibição canônica do casamento."""
        return f"Casamento de {self.bride_name} e {self.groom_name}"

    @property
    def is_completed(self) -> bool:
        """Indica se o casamento já foi realizado e concluído."""
        return self.status == self.StatusChoices.COMPLETED

    def get_days_until(self, reference_date: dt.date | None = None) -> int:
        """Retorna dias restantes até o casamento com suporte a data de referência."""
        if not self.date:
            return 0
        ref = reference_date or timezone.now().date()
        if self.date <= ref:
            return 0
        return (self.date - ref).days

    @property
    def planner_contract(self) -> Any:
        """Retorna o contrato de honorários de assessoria (PLANNER) formalizado do casamento."""
        if "_planner_contract_cache" in self.__dict__:
            return self.__dict__["_planner_contract_cache"]
        if (
            hasattr(self, "_prefetched_objects_cache")
            and "contracts" in self._prefetched_objects_cache
        ):
            for c in self.contracts.all():
                if getattr(c, "contract_type", None) == "PLANNER":
                    self.__dict__["_planner_contract_cache"] = c
                    return c
            self.__dict__["_planner_contract_cache"] = None
            return None
        from apps.contracts.interfaces import get_planner_contract_for_wedding

        contract = get_planner_contract_for_wedding(company=self.company, wedding=self)
        self.__dict__["_planner_contract_cache"] = contract
        return contract

    @planner_contract.setter
    def planner_contract(self, value: Any) -> None:
        self.__dict__["_planner_contract_cache"] = value

    @property
    def primary_signatory_client(self) -> Any:
        """
        Retorna o cliente (Client) configurado como signatário principal do contrato do casamento.
        """
        if (
            hasattr(self, "_prefetched_objects_cache")
            and "participants" in self._prefetched_objects_cache
        ):
            for participant in self.participants.all():
                if participant.is_primary_signatory:
                    return participant.client
            return None
        participant = (
            self.participants.filter(is_primary_signatory=True)
            .select_related("client")
            .first()
        )
        return participant.client if participant else None


class WeddingClient(TenantModel, WeddingOwnedMixin):
    """
    Associação entre um Casamento e um Cliente sob um papel específico (ADR-030).

    Permite mapear noivos, contratantes financeiros, signatários legais e outros
    envolvidos com rastreamento de quem assina o contrato e observações.
    """

    class RoleChoices(models.TextChoices):
        BRIDE = "BRIDE", "Noiva"
        GROOM = "GROOM", "Noivo"
        FINANCIAL_PAYER = "FINANCIAL_PAYER", "Contratante Financeiro"
        LEGAL_REPRESENTATIVE = "LEGAL_REPRESENTATIVE", "Representante Legal"
        OTHER = "OTHER", "Outro Envolvido"

    wedding = models.ForeignKey(
        "weddings.Wedding",
        on_delete=models.CASCADE,
        related_name="participants",
        verbose_name="Casamento",
    )
    client = models.ForeignKey(
        "clients.Client",
        on_delete=models.PROTECT,
        related_name="wedding_roles",
        verbose_name="Cliente",
    )
    role = models.CharField(
        max_length=30,
        choices=RoleChoices.choices,
        default=RoleChoices.BRIDE,
        verbose_name="Papel no Casamento",
    )
    is_primary_signatory = models.BooleanField(
        "Assina o Contrato?",
        default=False,
    )
    notes = models.TextField(
        "Observações",
        blank=True,
        default="",
    )

    class Meta:
        db_table = "wedding_participants"
        verbose_name = "Participante do Casamento"
        verbose_name_plural = "Participantes do Casamento"
        unique_together = [("wedding", "client", "role")]
        indexes = [
            models.Index(fields=["company", "wedding"]),
            models.Index(fields=["wedding", "role"]),
            models.Index(fields=["client"]),
        ]

    def __str__(self) -> str:
        return f"{self.client.name} - {self.get_role_display()} ({self.wedding})"

    def clean(self) -> None:
        """Valida a integridade do isolamento multi-tenant entre cliente e casamento."""
        super().clean()
        if hasattr(self, "company_id") and self.client_id:
            if self.company_id != self.client.company_id:
                raise ValidationError(
                    {"client": "Este cliente pertence a outra organização."}
                )

    def mark_as_primary_signatory(self, is_signatory: bool = True) -> None:
        """
        Define ou revoga a condição de signatário do contrato para o participante.

        Args:
            is_signatory: Se o participante deve assinar o instrumento contratual.
        """
        self.is_primary_signatory = is_signatory


WeddingStatusEnum = Wedding.StatusChoices

__all__ = [
    "Wedding",
    "WeddingClient",
    "WeddingStatusEnum",
    "validate_future_date",
]

sys.modules.setdefault("apps.weddings.models.wedding", sys.modules[__name__])
