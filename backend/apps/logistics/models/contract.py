"""
Modelo de Contratos do domínio logístico.

Responsabilidade: Gestão de contratos com fornecedores, incluindo valores, prazos e
documentação.

Referências: RF10, RF13
"""

from __future__ import annotations

from datetime import date
from typing import Any, ClassVar

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models

from apps.core.exceptions import BusinessRuleViolation
from apps.core.mixins import WeddingOwnedMixin
from apps.core.validators import MaxFileSizeValidator
from apps.logistics.managers import ContractQuerySet
from apps.tenants.models import TenantModel


class Contract(TenantModel, WeddingOwnedMixin):
    objects = ContractQuerySet.as_manager()  # type: ignore[assignment,misc]

    wedding = models.ForeignKey(
        "weddings.Wedding",
        on_delete=models.PROTECT,
        related_name="%(class)s_records",
    )

    class StatusChoices(models.TextChoices):
        DRAFT = "DRAFT", "Rascunho"
        PENDING = "PENDING", "Pendente"  # Aguardando assinaturas externas
        SIGNED = "SIGNED", "Assinado"
        CANCELED = "CANCELED", "Cancelado"

    supplier = models.ForeignKey(
        "logistics.Supplier",
        on_delete=models.CASCADE,
        related_name="contracts",
        verbose_name="Fornecedor",
    )

    # O VALOR DE FACE: Essencial para o Controle Máximo
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor Total do Contrato",
        help_text="Valor exato que consta no documento assinado",
    )

    name = models.CharField(max_length=255, verbose_name="Nome")
    description = models.TextField(
        blank=True, default="", verbose_name="Descrição do Contrato"
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT,
    )

    # Controle de prazos (RF13)
    expiration_date = models.DateField(null=True, blank=True)
    alert_days_before = models.PositiveIntegerField(default=30)

    # Metadados de Assinatura (Opcional - Controle Manual)
    # Como o sistema não assina, essas datas são preenchidas manualmente pelo Planner
    signed_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data da Assinatura",
        help_text="Data em que o contrato foi formalizado externamente",
    )

    pdf_file = models.FileField(
        upload_to="contracts/%Y/%m/",
        null=True,
        blank=True,
        verbose_name="Arquivo PDF",
        help_text="Formatos aceitos: PDF, PNG, JPEG. Tamanho máximo: 10MB.",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["pdf", "png", "jpg", "jpeg"],
                message="Tipo de arquivo não suportado. Use PDF, PNG ou JPEG.",
            ),
            MaxFileSizeValidator(max_size=10 * 1024 * 1024),
        ],
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="addendums",
        verbose_name="Contrato Original (Pai)",
        help_text="Vincula este contrato como aditivo de um contrato principal.",
    )

    class Meta:
        app_label = "logistics"
        verbose_name = "Contrato"
        verbose_name_plural = "Contratos"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["company", "wedding"]),
            models.Index(fields=["status"]),
        ]

    ALLOWED_TRANSITIONS: ClassVar[dict[str, list[str]]] = {
        "DRAFT": ["PENDING", "CANCELED"],
        "PENDING": ["SIGNED", "DRAFT", "CANCELED"],
        "SIGNED": ["CANCELED"],
        "CANCELED": ["DRAFT"],
    }

    def __str__(self) -> str:
        name = self.name or "Contrato"
        return (
            f"{name} - {self.supplier.name} ({self.wedding}) - R$ {self.total_amount}"
        )

    def clean(self) -> None:
        super().clean()
        self._clean_status_transition()
        self._clean_signed_requirements()
        self._clean_parent_hierarchy()

    def _clean_status_transition(self) -> None:
        if self.pk:
            orig = Contract.objects.filter(pk=self.pk).values("status").first()
            if orig and orig["status"] != self.status:
                allowed = self.ALLOWED_TRANSITIONS.get(orig["status"], [])
                if self.status not in allowed:
                    raise ValidationError(
                        f"Não é permitido transitar de '{orig['status']}' "
                        f"para '{self.status}'."
                    )

    # ── Métodos de Ciclo de Vida e Operações de Domínio ─────────────────

    def attach_file(self, file: Any) -> None:
        """Anexa o arquivo de contrato físico ou digital."""
        self.pdf_file = file

    def detach_file(self) -> None:
        """
        Remove o arquivo anexo do contrato.

        Raises:
            BusinessRuleViolation: Se o contrato estiver assinado.
        """
        if self.status == self.StatusChoices.SIGNED:
            raise BusinessRuleViolation(
                detail="Não é possível remover o arquivo de um contrato já assinado.",
                code="signed_contract_file_required",
            )
        if self.pdf_file:
            self.pdf_file.delete(save=False)
        self.pdf_file = None

    def set_parent(self, parent: Contract) -> None:
        """
        Define o contrato pai vinculando este como aditivo.

        Args:
            parent: Contrato principal que atuará como pai deste aditivo.

        Raises:
            BusinessRuleViolation: Se o contrato for pai de si mesmo ou de outro
                casamento.
        """
        if self.pk and parent.pk == self.pk:
            raise BusinessRuleViolation(
                detail="Um contrato não pode ser pai de si mesmo.",
                code="contract_self_parent",
            )
        if self.wedding_id and parent.wedding_id != self.wedding_id:
            raise BusinessRuleViolation(
                detail="O contrato pai deve pertencer ao mesmo casamento.",
                code="contract_cross_wedding_parent",
            )
        if self.pk:
            current: Contract | None = parent
            while current:
                if current.pk == self.pk:
                    raise BusinessRuleViolation(
                        detail=(
                            "Não é possível vincular um contrato pai que é "
                            "descendente deste contrato."
                        ),
                        code="contract_circular_parent",
                    )
                current = current.parent
        self.parent = parent

    def remove_parent(self) -> None:
        """Desvincula este contrato de seu contrato principal tornando-o autônomo."""
        self.parent = None

    def can_transition_to(self, target_status: str | StatusChoices) -> bool:
        """Verifica se a transição para o status informado é válida.

        Args:
            target_status: Status de destino a ser avaliado.

        Returns:
            True se a transição for permitida, False caso contrário.
        """
        target = str(target_status)
        if self.status == target:
            return True
        allowed = self.ALLOWED_TRANSITIONS.get(self.status, [])
        return target in allowed

    def transition_to(self, target_status: str | StatusChoices) -> None:
        """Executa a transição de status validando as regras de negócio de domínio.

        Args:
            target_status: Status de destino para a transição.

        Raises:
            BusinessRuleViolation: Se a transição de status não for permitida.
        """
        target = str(target_status)
        if self.status == target:
            return

        if not self.can_transition_to(target):
            raise BusinessRuleViolation(
                detail=f"Não é permitido transitar de '{self.status}' para '{target}'.",
                code="contract_invalid_status_transition",
            )

        self.status = str(target_status)

    def send_to_pending(self) -> None:
        """Transita o contrato para pendente de assinaturas externas."""
        self.transition_to(self.StatusChoices.PENDING)

    def sign(self, *, signed_date: date | None = None, pdf_file: Any = None) -> None:
        """Formaliza a assinatura do contrato externamente.

        Args:
            signed_date: Data opcional em que o contrato foi assinado.
            pdf_file: Arquivo PDF ou chave de arquivo opcional do documento assinado.
        """
        if signed_date is not None:
            self.signed_date = signed_date
        if pdf_file is not None:
            self.pdf_file = pdf_file
        self.transition_to(self.StatusChoices.SIGNED)

    def cancel(self) -> None:
        """Cancela o contrato."""
        self.transition_to(self.StatusChoices.CANCELED)

    def revert_to_draft(self) -> None:
        """Reverte o contrato para rascunho."""
        self.transition_to(self.StatusChoices.DRAFT)

    # ── Propriedades de Domínio e Conveniência ───────────────────────────

    @property
    def is_addendum(self) -> bool:
        """Indica se este contrato é um aditivo (possui contrato pai)."""
        return self.parent_id is not None

    @property
    def has_file(self) -> bool:
        """Indica se o contrato possui arquivo PDF anexado."""
        return bool(self.pdf_file)

    @property
    def file_name(self) -> str | None:
        """Retorna o nome do arquivo anexado ao contrato, se houver."""
        if self.pdf_file and self.pdf_file.name:
            return self.pdf_file.name.split("/")[-1]
        return None

    def _clean_signed_requirements(self) -> None:
        if self.status == self.StatusChoices.SIGNED:
            if not self.pdf_file:
                raise ValidationError(
                    "Um contrato marcado como ASSINADO exige o upload do arquivo PDF."
                )
            if not self.total_amount or self.total_amount <= 0:
                raise ValidationError(
                    "Um contrato marcado como ASSINADO deve ter um valor total "
                    "positivo."
                )
            if not self.signed_date:
                raise ValidationError("Informe a data em que o contrato foi assinado.")

    def _clean_parent_hierarchy(self) -> None:
        if self.parent:
            if self.pk and self.parent_id == self.pk:
                raise ValidationError("Um contrato não pode ser pai de si mesmo.")
            if self.wedding_id and self.parent.wedding_id != self.wedding_id:
                raise ValidationError("O contrato pai pertence a outro casamento.")
            if self.pk:
                current: Contract | None = self.parent
                while current:
                    if current.pk == self.pk:
                        raise ValidationError(
                            "Não é possível vincular um contrato pai que é "
                            "descendente deste contrato."
                        )
                    current = current.parent
