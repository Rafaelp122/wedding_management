"""
Modelo unificado de Contratos do sistema de casamentos.

Responsabilidade: Gestão integral de contratos com fornecedores e contratos de honorários
de assessoria cerimonial (ADR-030, ADR-031), unificando Contract e Contract sob
um único Aggregate Root com suporte a termos aditivos e multi-tenancy estrito.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, ClassVar

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models

from apps.contracts.managers import ContractQuerySet
from apps.contracts.mixins import SignableDocumentMixin
from apps.core.exceptions import BusinessRuleViolation
from apps.core.mixins import WeddingOwnedMixin
from apps.core.validators import MaxFileSizeValidator
from apps.tenants.models import TenantModel


class Contract(TenantModel, WeddingOwnedMixin, SignableDocumentMixin):
    """
    Entidade unificada de Contratos (ADR-030 / ADR-031).

    Representa tanto instrumentos jurídicos de honorários da assessoria (PLANNER)
    quanto contratos com prestadores logísticos externos (SUPPLIER).
    """

    objects = ContractQuerySet.as_manager()  # type: ignore[assignment,misc]

    class ContractTypeChoices(models.TextChoices):
        PLANNER = "PLANNER", "Assessoria"
        SUPPLIER = "SUPPLIER", "Fornecedor"

    class ServiceTierChoices(models.TextChoices):
        COMPLETA = "COMPLETA", "Assessoria Completa"
        PARCIAL = "PARCIAL", "Assessoria Parcial"
        FINAL = "FINAL", "Assessoria do Dia/Final"

    class StatusChoices(models.TextChoices):
        DRAFT = "DRAFT", "Rascunho"
        PENDING = "PENDING", "Pendente"
        SIGNED = "SIGNED", "Assinado"
        CANCELED = "CANCELED", "Cancelado"

    wedding = models.ForeignKey(
        "weddings.Wedding",
        on_delete=models.PROTECT,
        related_name="contracts",
        verbose_name="Casamento",
    )

    contract_type = models.CharField(
        max_length=20,
        choices=ContractTypeChoices.choices,
        default=ContractTypeChoices.SUPPLIER,
        verbose_name="Tipo de Contrato",
    )

    service_tier = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=ServiceTierChoices.choices,
        verbose_name="Tipo de Assessoria",
    )

    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="contracts",
        verbose_name="Fornecedor",
    )

    client = models.ForeignKey(
        "clients.Client",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contracts",
        verbose_name="Contratante Principal",
    )

    name = models.CharField(max_length=255, verbose_name="Nome")
    description = models.TextField(
        blank=True, default="", verbose_name="Descrição do Contrato"
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor Total do Contrato",
        help_text="Valor nominal de face que consta no documento formalizado",
    )

    installments_count = models.PositiveIntegerField(
        default=1,
        verbose_name="Número de Parcelas",
    )

    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT,
        verbose_name="Status do Contrato",
    )

    expiration_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Vencimento/Validade",
    )
    alert_days_before = models.PositiveIntegerField(
        default=30,
        verbose_name="Dias de Alerta Prévio",
    )

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

    ALLOWED_TRANSITIONS: ClassVar[dict[str, list[str]]] = {
        StatusChoices.DRAFT.value: [
            StatusChoices.PENDING.value,
            StatusChoices.CANCELED.value,
        ],
        StatusChoices.PENDING.value: [
            StatusChoices.SIGNED.value,
            StatusChoices.DRAFT.value,
            StatusChoices.CANCELED.value,
        ],
        StatusChoices.SIGNED.value: [
            StatusChoices.CANCELED.value,
        ],
        StatusChoices.CANCELED.value: [
            StatusChoices.DRAFT.value,
        ],
    }

    PLANNER_ALLOWED_TRANSITIONS: ClassVar[dict[str, list[str]]] = {
        StatusChoices.DRAFT.value: [
            StatusChoices.PENDING.value,
            StatusChoices.SIGNED.value,
            StatusChoices.CANCELED.value,
        ],
        StatusChoices.PENDING.value: [
            StatusChoices.SIGNED.value,
            StatusChoices.DRAFT.value,
            StatusChoices.CANCELED.value,
        ],
        StatusChoices.SIGNED.value: [
            StatusChoices.CANCELED.value,
        ],
        StatusChoices.CANCELED.value: [
            StatusChoices.DRAFT.value,
        ],
    }

    class Meta:
        db_table = "contracts"
        verbose_name = "Contrato"
        verbose_name_plural = "Contratos"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["company", "wedding"]),
            models.Index(fields=["company", "contract_type"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        if self.contract_type == self.ContractTypeChoices.PLANNER:
            tier = (
                self.get_service_tier_display() if self.service_tier else "Assessoria"
            )
            return f"Contrato de Assessoria ({tier}) - {self.wedding}"
        supplier_name = self.supplier.name if self.supplier else "Sem fornecedor"
        contract_name = self.name or "Contrato"
        return f"{contract_name} - {supplier_name} ({self.wedding}) - R$ {self.total_amount}"

    def clean(self) -> None:
        """Valida invariantes de integridade e regras de negócio do contrato."""
        super().clean()
        errors: dict[str, list[str]] = {}

        for cleaner in (
            self._clean_status_transition,
            self._clean_type_invariants,
            self._clean_value_invariants,
            self._clean_signed_requirements,
            self._clean_tenant_invariants,
        ):
            try:
                cleaner()
            except ValidationError as exc:
                if hasattr(exc, "message_dict"):
                    for k, v in exc.message_dict.items():
                        errors.setdefault(k, []).extend(
                            v if isinstance(v, list) else [v]
                        )
                elif hasattr(exc, "messages"):
                    errors.setdefault("__all__", []).extend(exc.messages)
                else:
                    errors.setdefault("__all__", []).append(str(exc))

        if errors:
            raise ValidationError(errors)

    def _clean_status_transition(self) -> None:
        if self.pk:
            orig_qs = Contract.objects.filter(pk=self.pk)
            if getattr(self, "company_id", None):
                orig_qs = orig_qs.filter(company_id=self.company_id)
            orig = orig_qs.values("status").first()
            if orig and orig["status"] != self.status:
                allowed_dict = (
                    self.PLANNER_ALLOWED_TRANSITIONS
                    if self.contract_type == self.ContractTypeChoices.PLANNER
                    else self.ALLOWED_TRANSITIONS
                )
                allowed = allowed_dict.get(orig["status"], [])
                if self.status not in allowed:
                    raise ValidationError(
                        f"Não é permitido transitar de '{orig['status']}' para '{self.status}'."
                    )

    def _clean_type_invariants(self) -> None:
        if self.contract_type == self.ContractTypeChoices.SUPPLIER:
            if not self.supplier_id:
                raise ValidationError(
                    {
                        "supplier": "Contratos de fornecedores exigem um fornecedor vinculado."
                    }
                )
        elif self.contract_type == self.ContractTypeChoices.PLANNER:
            if self.supplier_id:
                raise ValidationError(
                    {
                        "supplier": "Contratos de assessoria não devem ter fornecedor vinculado."
                    }
                )
            if not self.service_tier:
                raise ValidationError(
                    {
                        "service_tier": "Contratos de assessoria exigem o nível de serviço (service_tier)."
                    }
                )

    def _clean_value_invariants(self) -> None:
        if self.total_amount is not None and self.total_amount < Decimal("0.00"):
            msg = (
                "O valor dos honorários não pode ser negativo."
                if self.contract_type == self.ContractTypeChoices.PLANNER
                else "O valor total do contrato não pode ser negativo."
            )
            raise ValidationError({"total_amount": msg, "effective_amount": msg})

        if self.installments_count is not None and self.installments_count < 1:
            raise ValidationError(
                {"installments_count": "O número de parcelas deve ser de no mínimo 1."}
            )

    def _clean_signed_requirements(self) -> None:
        if self.status == self.StatusChoices.SIGNED:
            errors: dict[str, str] = {}
            if (
                self.contract_type == self.ContractTypeChoices.SUPPLIER
                and not self.pdf_file
            ):
                errors["pdf_file"] = (
                    "Um contrato marcado como ASSINADO exige o upload do arquivo PDF."
                )
            if not self.signed_date:
                errors["signed_date"] = (
                    "Contratos assinados exigem a data de assinatura."
                    if self.contract_type == self.ContractTypeChoices.PLANNER
                    else "Informe a data em que o contrato foi assinado."
                )
            if not self.total_amount or self.total_amount <= 0:
                errors["total_amount"] = (
                    "Um contrato marcado como ASSINADO deve ter um valor total positivo."
                )
            if errors:
                raise ValidationError(errors)

    def _clean_tenant_invariants(self) -> None:
        if self.supplier_id and hasattr(self, "company_id") and self.company_id:
            if self.supplier and self.supplier.company_id != self.company_id:
                raise ValidationError(
                    {"supplier": "Fornecedor pertence a outra organização."}
                )
        if self.client_id and hasattr(self, "company_id") and self.company_id:
            if self.client and self.client.company_id != self.company_id:
                raise ValidationError(
                    {"client": "Cliente pertence a outra organização."}
                )
        if self.wedding_id and hasattr(self, "company_id") and self.company_id:
            if self.wedding and self.wedding.company_id != self.company_id:
                raise ValidationError(
                    {"wedding": "Casamento pertence a outra organização."}
                )

    # ── Métodos de Ciclo de Vida e Operações de Domínio ─────────────────

    def attach_file(self, file: Any) -> None:
        """Anexa o arquivo de contrato físico ou digital."""
        self.pdf_file = file

    def detach_file(self) -> None:
        """Remove o arquivo anexo do contrato.

        Raises:
            BusinessRuleViolation: Se o contrato estiver formalmente assinado.
        """
        if self.status == self.StatusChoices.SIGNED:
            raise BusinessRuleViolation(
                detail="Não é possível remover o arquivo de um contrato já assinado.",
                code="signed_contract_file_required",
            )
        if self.pdf_file:
            self.pdf_file.delete(save=False)
        self.pdf_file = None

    def send_to_pending(self) -> None:
        """Transita o contrato para aguardando assinaturas externas."""
        self.transition_to(self.StatusChoices.PENDING)

    def revert_to_draft(self) -> None:
        """Reverte o contrato para rascunho de trabalho."""
        self.transition_to(self.StatusChoices.DRAFT)

    # ── Propriedades de Domínio e Compatibilidade ───────────────────────

    @property
    def base_amount(self) -> Decimal:
        """Retorna o valor de face original do contrato."""
        if hasattr(self, "_annotated_base_amount"):
            return self._annotated_base_amount
        return self.total_amount or Decimal("0.00")

    @base_amount.setter
    def base_amount(self, value: Decimal) -> None:
        self._annotated_base_amount = value

    @property
    def addendums_total(self) -> Decimal:
        """Retorna a soma de todos os aditivos assinados (SIGNED)."""
        if hasattr(self, "_annotated_addendums_total"):
            return self._annotated_addendums_total
        if (
            hasattr(self, "_prefetched_objects_cache")
            and "addendums" in self._prefetched_objects_cache
        ):
            return sum(
                (a.amount for a in self.addendums.all() if a.status == "SIGNED"),
                Decimal("0.00"),
            )
        total = self.addendums.filter(status="SIGNED").aggregate(models.Sum("amount"))[
            "amount__sum"
        ]
        return total or Decimal("0.00")

    @addendums_total.setter
    def addendums_total(self, value: Decimal) -> None:
        self._annotated_addendums_total = value

    @property
    def effective_amount(self) -> Decimal:
        """Retorna o valor efetivo consolidado (base_amount + addendums_total)."""
        if hasattr(self, "_annotated_effective_amount"):
            return self._annotated_effective_amount
        return self.base_amount + self.addendums_total

    @effective_amount.setter
    def effective_amount(self, value: Decimal) -> None:
        self._annotated_effective_amount = value
