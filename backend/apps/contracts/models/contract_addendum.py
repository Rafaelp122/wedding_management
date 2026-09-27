"""
Modelo de Termo Aditivo Contratual (ContractAddendum).

Responsabilidade: Gestão de alterações de valor, escopo ou prazos contratuais formalizados
como entidades filhas dedicadas (1:N) de contratos (ADR-030 / RFC-001).
"""

from __future__ import annotations

from decimal import Decimal
from typing import ClassVar

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models

from apps.contracts.managers import ContractAddendumQuerySet
from apps.contracts.mixins import SignableDocumentMixin
from apps.core.mixins import WeddingOwnedMixin
from apps.core.validators import MaxFileSizeValidator
from apps.tenants.models import TenantModel


class ContractAddendum(TenantModel, WeddingOwnedMixin, SignableDocumentMixin):
    """
    Entidade filha de termos aditivos contratuais (RFC-001 / ADR-030).
    Vinculada exclusivamente a um contrato principal de forma acíclica.
    """

    objects = ContractAddendumQuerySet.as_manager()  # type: ignore[assignment,misc]

    class StatusChoices(models.TextChoices):
        PENDING = "PENDING", "Pendente"
        SIGNED = "SIGNED", "Assinado"
        CANCELED = "CANCELED", "Cancelado"

    contract = models.ForeignKey(
        "contracts.Contract",
        on_delete=models.CASCADE,
        related_name="addendums",
        verbose_name="Contrato Principal",
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor do Aditivo",
    )

    signed_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data da Assinatura",
    )

    justification = models.TextField(
        verbose_name="Justificativa do Aditivo",
    )

    pdf_file = models.FileField(
        upload_to="contracts/addendums/%Y/%m/",
        null=True,
        blank=True,
        verbose_name="Arquivo PDF do Aditivo",
        help_text="Formatos aceitos: PDF, PNG, JPEG. Tamanho máximo: 10MB.",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["pdf", "png", "jpg", "jpeg"],
                message="Tipo de arquivo não suportado. Use PDF, PNG ou JPEG.",
            ),
            MaxFileSizeValidator(max_size=10 * 1024 * 1024),
        ],
    )

    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
    )

    ALLOWED_TRANSITIONS: ClassVar[dict[str, list[str]]] = {
        StatusChoices.PENDING.value: [
            StatusChoices.SIGNED.value,
            StatusChoices.CANCELED.value,
        ],
        StatusChoices.SIGNED.value: [StatusChoices.CANCELED.value],
        StatusChoices.CANCELED.value: [],
    }

    class Meta:
        db_table = "contract_addendums"
        verbose_name = "Termo Aditivo"
        verbose_name_plural = "Termos Aditivos"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["company", "wedding"]),
            models.Index(fields=["contract"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"Aditivo #{self.pk or self.uuid} - {self.contract} (R$ {self.amount})"

    def clean(self) -> None:
        """Valida regras de integridade e transições de estado do aditivo."""
        super().clean()
        self._clean_status_transition()
        self._clean_invariants()
        self._clean_contract_alignment()

    def _clean_status_transition(self) -> None:
        if self.pk:
            orig = ContractAddendum.objects.filter(pk=self.pk).values("status").first()
            if orig and orig["status"] != self.status:
                allowed = self.ALLOWED_TRANSITIONS.get(orig["status"], [])
                if self.status not in allowed:
                    raise ValidationError(
                        f"Não é permitido transitar de '{orig['status']}' para '{self.status}'."
                    )

    def _clean_invariants(self) -> None:
        if self.amount is None or self.amount <= Decimal("0.00"):
            raise ValidationError({"amount": "O valor do aditivo deve ser positivo."})

        if self.status == self.StatusChoices.SIGNED and not self.signed_date:
            raise ValidationError(
                {
                    "signed_date": "A data de assinatura é obrigatória para aditivos assinados."
                }
            )

        if not self.justification or not self.justification.strip():
            raise ValidationError(
                {
                    "justification": (
                        "A justificativa do aditivo é obrigatória e não pode "
                        "conter apenas espaços."
                    )
                }
            )

    def _clean_contract_alignment(self) -> None:
        if hasattr(self, "contract") and self.contract:
            if not self.wedding_id:
                self.wedding = self.contract.wedding
            elif self.contract.wedding_id != self.wedding_id:
                raise ValidationError(
                    {
                        "wedding": "O aditivo deve pertencer ao mesmo casamento do contrato principal."
                    }
                )

            if not self.company_id:
                self.company = self.contract.company
            elif self.contract.company_id != self.company_id:
                raise ValidationError(
                    {
                        "company": "O aditivo deve pertencer à mesma empresa do contrato principal."
                    }
                )
