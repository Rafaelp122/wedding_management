"""
Modelo de Itens do domínio logístico.

Responsabilidade: Gestão de itens de logística, representando necessidades físicas e
serviços contratados.

Referências: RF07-RF08
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from django.core.exceptions import ValidationError
from django.db import models

from apps.core.exceptions import BusinessRuleViolation, DomainIntegrityError
from apps.core.mixins import WeddingOwnedMixin
from apps.logistics.managers import ItemQuerySet
from apps.tenants.models import TenantModel


if TYPE_CHECKING:
    from apps.contracts.models import Contract


class SupplyItem(TenantModel, WeddingOwnedMixin):
    """
    Item de suprimento e logística (RF-15 / RFC-001).
    Representa a necessidade física ou o serviço contratado sob 3 dimensões:
    escopo (desejado vs descartado com justificativa), cotação/contratação e entrega física.
    """

    objects = ItemQuerySet.as_manager()  # type: ignore[assignment,misc]

    ALLOWED_TRANSITIONS: ClassVar[dict[str, list[str]]] = {
        "PENDING": ["IN_PROGRESS"],
        "IN_PROGRESS": ["DONE", "PENDING"],
        "DONE": ["IN_PROGRESS"],
    }

    class ScopeStatus(models.TextChoices):
        DESIRED = "DESIRED", "Desejado"
        INCLUDED = "INCLUDED", "Incluído"
        DISCARDED = "DISCARDED", "Descartado"

    class ProcurementStatus(models.TextChoices):
        A_COTAR = "A_COTAR", "A Cotar"
        EM_NEGOCIACAO = "EM_NEGOCIACAO", "Em Negociação"
        CONTRATADO = "CONTRATADO", "Contratado"

    class DeliveryStatus(models.TextChoices):
        PENDING = "PENDING", "Pendente"
        DELIVERED = "DELIVERED", "Entregue"
        RETURNED = "RETURNED", "Devolvido"

    class AcquisitionStatus(models.TextChoices):
        PENDING = "PENDING", "Pendente"
        IN_PROGRESS = "IN_PROGRESS", "Em Andamento"
        DONE = "DONE", "Concluído"

    # Relação N:1 - Muitos itens podem pertencer ao mesmo contrato
    contract = models.ForeignKey(
        "contracts.Contract",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="items",
        verbose_name="Contrato",
        help_text="Contrato associado a este item",
    )

    name = models.CharField(max_length=255, verbose_name="Nome do Item")
    description = models.TextField(blank=True, verbose_name="Descrição/Especificações")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantidade")

    scope_status = models.CharField(
        max_length=20,
        choices=ScopeStatus.choices,
        default=ScopeStatus.INCLUDED,
        verbose_name="Status de Escopo",
    )
    rejection_reason = models.TextField(
        blank=True,
        default="",
        verbose_name="Motivo do Descarte",
    )
    procurement_status = models.CharField(
        max_length=20,
        choices=ProcurementStatus.choices,
        default=ProcurementStatus.CONTRATADO,
        verbose_name="Status de Cotação",
    )
    delivery_status = models.CharField(
        max_length=20,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.PENDING,
        verbose_name="Status de Entrega Física",
    )

    acquisition_status = models.CharField(
        max_length=20,
        choices=AcquisitionStatus.choices,
        default=AcquisitionStatus.PENDING,
        verbose_name="Status de Entrega/Logística",
    )

    class Meta:
        app_label = "logistics"
        db_table = "logistics_item"
        verbose_name = "Item de Suprimento"
        verbose_name_plural = "Itens de Suprimento"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["company", "wedding"]),
            models.Index(fields=["acquisition_status"]),
            models.Index(fields=["company", "scope_status"]),
            models.Index(fields=["company", "delivery_status"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.quantity}x)"

    def clean(self) -> None:
        super().clean()
        if self.quantity is not None and self.quantity < 1:
            raise ValidationError(
                {"quantity": "A quantidade deve ser de no mínimo 1 unidade."}
            )
        if (
            self.contract
            and self.wedding_id
            and self.contract.wedding_id != self.wedding_id
        ):
            raise ValidationError(
                {
                    "contract": (
                        "O contrato informado não pertence ao casamento deste item."
                    )
                }
            )
        if self.scope_status == self.ScopeStatus.DISCARDED and not (
            self.rejection_reason and self.rejection_reason.strip()
        ):
            raise ValidationError(
                {
                    "rejection_reason": (
                        "O motivo do descarte é obrigatório ao marcar o item como descartado."
                    )
                }
            )
        if self.pk:
            orig = (
                SupplyItem.objects.filter(pk=self.pk)
                .values("acquisition_status")
                .first()
            )
            if orig and orig["acquisition_status"] != self.acquisition_status:
                allowed = self.ALLOWED_TRANSITIONS.get(orig["acquisition_status"], [])
                if self.acquisition_status not in allowed:
                    raise ValidationError(
                        f"Não é permitido transitar de "
                        f"'{orig['acquisition_status']}' para "
                        f"'{self.acquisition_status}'."
                    )

    # ── Métodos de Domínio e Ciclo de Vida da Entidade ──────────────────

    def discard(self, reason: str) -> None:
        """Descarta o item do escopo registrando compulsoriamente a justificativa (RF-15)."""
        if not reason or not reason.strip():
            raise BusinessRuleViolation(
                detail="O motivo do descarte é obrigatório ao marcar o item como descartado.",
                code="supply_item_rejection_reason_required",
            )
        self.scope_status = self.ScopeStatus.DISCARDED
        self.rejection_reason = reason.strip()

    def include(self) -> None:
        """Reintegra o item ao escopo aprovado do evento."""
        self.scope_status = self.ScopeStatus.INCLUDED
        self.rejection_reason = ""

    def mark_as_delivered(self) -> None:
        """Registra a conferência física e entrega do material no local (RF-15)."""
        self.delivery_status = self.DeliveryStatus.DELIVERED

    def mark_as_returned(self) -> None:
        """Registra a devolução física do material após o evento."""
        self.delivery_status = self.DeliveryStatus.RETURNED

    def assign_contract(self, contract: Contract) -> None:
        """
        Associa o item a um contrato garantindo consistência de casamento.

        Args:
            contract: Contrato a ser vinculado.

        Raises:
            BusinessRuleViolation: Se o contrato pertencer a outro casamento.
        """
        if self.wedding_id and contract.wedding_id != self.wedding_id:
            raise DomainIntegrityError(
                detail="O contrato informado não pertence ao casamento deste item.",
                code="item_contract_wedding_mismatch",
            )
        self.contract = contract

    def detach_contract(self) -> None:
        """Remove o vínculo do item com seu contrato."""
        self.contract = None

    def can_transition_to(self, target_status: str | AcquisitionStatus) -> bool:
        """Verifica se a transição para o status de aquisição informado é válida."""
        target = str(target_status)
        if self.acquisition_status == target:
            return True
        allowed = self.ALLOWED_TRANSITIONS.get(self.acquisition_status, [])
        return target in allowed

    def transition_to(self, target_status: str | AcquisitionStatus) -> None:
        """Executa a transição de status de aquisição validando as regras do domínio."""
        target = str(target_status)
        if self.acquisition_status == target:
            return

        if not self.can_transition_to(target):
            raise BusinessRuleViolation(
                detail=(
                    f"Não é permitido transitar de '{self.acquisition_status}' "
                    f"para '{target}'."
                ),
                code="item_invalid_status_transition",
            )

        self.acquisition_status = str(target_status)

    def start(self) -> None:
        """Inicia a aquisição/execução do item, transitando para EM ANDAMENTO."""
        self.transition_to(self.AcquisitionStatus.IN_PROGRESS)

    def complete(self) -> None:
        """Conclui a aquisição do item, transitando para CONCLUÍDO."""
        self.transition_to(self.AcquisitionStatus.DONE)

    def reopen(self) -> None:
        """Reabre item concluído, transitando de DONE para IN_PROGRESS."""
        self.transition_to(self.AcquisitionStatus.IN_PROGRESS)

    def revert_to_pending(self) -> None:
        """Reverte o item em andamento de volta para PENDENTE."""
        self.transition_to(self.AcquisitionStatus.PENDING)


# Alias canônico para manter retrocompatibilidade com importações anteriores (ADR-031 / RFC-001)
Item = SupplyItem
