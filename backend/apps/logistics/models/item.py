"""
Modelo de Itens do domínio logístico.

Responsabilidade: Gestão de itens de logística, representando necessidades físicas e
serviços contratados.

Referências: RF07-RF08
"""

from typing import ClassVar

from django.core.exceptions import ValidationError
from django.db import models

from apps.core.exceptions import BusinessRuleViolation, DomainIntegrityError
from apps.core.mixins import WeddingOwnedMixin
from apps.logistics.managers import ItemQuerySet
from apps.tenants.models import TenantModel

from .contract import Contract


class Item(TenantModel, WeddingOwnedMixin):
    """
    Item de logística (RF07-RF08).
    Representa a necessidade física ou o serviço contratado.
    """

    objects = ItemQuerySet.as_manager()  # type: ignore[assignment,misc]

    ALLOWED_TRANSITIONS: ClassVar[dict[str, list[str]]] = {
        "PENDING": ["IN_PROGRESS"],
        "IN_PROGRESS": ["DONE", "PENDING"],
        "DONE": ["IN_PROGRESS"],
    }

    class AcquisitionStatus(models.TextChoices):
        PENDING = "PENDING", "Pendente"
        IN_PROGRESS = "IN_PROGRESS", "Em Andamento"
        DONE = "DONE", "Concluído"

    # Relação N:1 - Muitos itens podem pertencer ao mesmo contrato
    contract = models.ForeignKey(
        Contract,
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

    acquisition_status = models.CharField(
        max_length=20,
        choices=AcquisitionStatus.choices,
        default=AcquisitionStatus.PENDING,
        verbose_name="Status de Entrega/Logística",
    )

    class Meta:
        app_label = "logistics"
        verbose_name = "Item"
        verbose_name_plural = "Itens"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["company", "wedding"]),
            models.Index(fields=["acquisition_status"]),
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
        if self.pk:
            orig = Item.objects.filter(pk=self.pk).values("acquisition_status").first()
            if orig and orig["acquisition_status"] != self.acquisition_status:
                allowed = self.ALLOWED_TRANSITIONS.get(orig["acquisition_status"], [])
                if self.acquisition_status not in allowed:
                    raise ValidationError(
                        f"Não é permitido transitar de "
                        f"'{orig['acquisition_status']}' para "
                        f"'{self.acquisition_status}'."
                    )

    # ── Métodos de Domínio e Ciclo de Vida da Entidade ──────────────────

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
        """Verifica se a transição para o status de aquisição informado é válida.

        Args:
            target_status: Status de destino a ser avaliado.

        Returns:
            True se a transição for permitida, False caso contrário.
        """
        target = str(target_status)
        if self.acquisition_status == target:
            return True
        allowed = self.ALLOWED_TRANSITIONS.get(self.acquisition_status, [])
        return target in allowed

    def transition_to(self, target_status: str | AcquisitionStatus) -> None:
        """Executa a transição de status de aquisição validando as regras do domínio.

        Args:
            target_status: Status de destino para a transição.

        Raises:
            BusinessRuleViolation: Se a transição de status não for permitida.
        """
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
