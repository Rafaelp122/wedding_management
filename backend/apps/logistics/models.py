"""
Models do domínio logístico.

Responsabilidade: Gestão de fornecedores, itens de logística e contratos.
Referências: RF07-RF13
"""

from django.core.validators import MaxLengthValidator
from django.db import models

from apps.core.models import SoftDeleteModel


class Supplier(SoftDeleteModel):
    """
    Fornecedores de produtos e serviços para casamentos (RF09).
    Centraliza informações de contato e histórico de relacionamento.
    """

    # Informações básicas
    name = models.CharField(
        max_length=255,
        verbose_name="Nome",
        help_text="Nome do fornecedor ou empresa",
    )
    cnpj = models.CharField(
        max_length=18,
        blank=True,
        verbose_name="CNPJ",
        help_text="Formato: 00.000.000/0000-00",
    )

    # Contato
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Telefone",
        help_text="Formato: (00) 00000-0000",
    )
    email = models.EmailField(
        blank=True,
        verbose_name="E-mail",
    )
    website = models.URLField(
        blank=True,
        verbose_name="Website",
    )

    # Endereço
    address = models.TextField(
        blank=True,
        verbose_name="Endereço",
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Cidade",
    )
    state = models.CharField(
        max_length=2,
        blank=True,
        verbose_name="Estado (UF)",
        validators=[MaxLengthValidator(2)],
    )

    # Gestão (RF09)
    notes = models.TextField(
        blank=True,
        verbose_name="Observações",
        help_text="Anotações internas sobre o fornecedor",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Fornecedor disponível para novos contratos",
    )

    class Meta:
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["city", "state"]),
        ]

    def __str__(self):
        return self.name

    @property
    def full_address(self):
        """Retorna endereço completo formatado."""
        parts = [self.address, self.city]
        if self.state:
            parts.append(self.state)
        return ", ".join(filter(None, parts))


class Contract(SoftDeleteModel):
    """
    Contratos formais com fornecedores (RF10-RF13).
    O contrato é o documento jurídico que pode englobar vários itens/serviços.
    """

    class StatusChoices(models.TextChoices):
        DRAFT = "DRAFT", "Rascunho"
        PENDING = "PENDING", "Pendente"
        SIGNED = "SIGNED", "Assinado"
        CANCELED = "CANCELED", "Cancelado"

    # O contrato pertence a um casamento e a um fornecedor específico
    wedding = models.ForeignKey(
        "weddings.Wedding",
        on_delete=models.CASCADE,
        related_name="contracts",
        verbose_name="Casamento",
    )
    supplier = models.ForeignKey(
        "logistics.Supplier",  # Assume-se que Supplier foi movido para este app
        on_delete=models.CASCADE,
        related_name="contracts",
        verbose_name="Fornecedor",
    )

    description = models.TextField(blank=True, verbose_name="Descrição do Contrato")
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT,
        verbose_name="Status",
    )

    # Datas e Alertas (RF13)
    expiration_date = models.DateField(
        null=True, blank=True, verbose_name="Data de Vencimento"
    )
    alert_days_before = models.PositiveIntegerField(
        default=30, verbose_name="Alertar Dias Antes"
    )

    # Assinaturas Digitais/Controlo (RF12)
    planner_signed_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Assinado pelo Planner"
    )
    supplier_signed_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Assinado pelo Fornecedor"
    )
    couple_signed_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Assinado pelos Noivos"
    )

    # Arquivo (RF10)
    pdf_file = models.FileField(
        upload_to="contracts/%Y/%m/", null=True, blank=True, verbose_name="Arquivo PDF"
    )

    class Meta:
        verbose_name = "Contrato"
        verbose_name_plural = "Contratos"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Contrato {self.id} - {self.supplier.name} ({self.wedding})"

    @property
    def is_fully_signed(self):
        """Garante que a 'visão descomplicada' saiba se o papel jurídico está em
        ordem."""
        return all(
            [self.planner_signed_at, self.supplier_signed_at, self.couple_signed_at]
        )

    def clean(self):
        """Validações de negócio."""
        super().clean()
        from django.core.exceptions import ValidationError

        if self.status == self.StatusChoices.SIGNED and not self.pdf_file:
            raise ValidationError("Contrato ASSINADO precisa ter arquivo PDF anexado")

    def save(self, *args, **kwargs):
        # Auto-update status quando todos assinaram
        if self.is_fully_signed and self.status != self.StatusChoices.SIGNED:
            self.status = self.StatusChoices.SIGNED

        self.full_clean()
        super().save(*args, **kwargs)


class Item(SoftDeleteModel):
    """
    Item de logística (RF07-RF08).
    Representa a necessidade física ou o serviço contratado.
    """

    class AcquisitionStatus(models.TextChoices):
        PENDING = "PENDING", "Pendente"
        IN_PROGRESS = "IN_PROGRESS", "Em Andamento"
        DONE = "DONE", "Concluído"

    wedding = models.ForeignKey(
        "weddings.Wedding",
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Casamento",
    )

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

    # Ligação necessária para o Dashboard Financeiro saber onde este item 'mora'
    budget_category = models.ForeignKey(
        "finances.BudgetCategory",
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Categoria Orçamental",
    )

    class Meta:
        verbose_name = "Item"
        verbose_name_plural = "Itens"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.quantity}x)"

    @property
    def supplier(self):
        """Fornecedor vem do contrato associado."""
        return self.contract.supplier if self.contract else None
