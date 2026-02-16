"""
Modelo de Orçamento do domínio financeiro.

Responsabilidade: Gestão do orçamento mestre, definindo o teto financeiro global
do casamento.

Referência: RF03
"""

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from apps.core.mixins import WeddingOwnedMixin
from apps.core.models import BaseModel


class Budget(BaseModel, WeddingOwnedMixin):
    """
    Orçamento mestre (RF03).
    Define o teto financeiro global do casamento.

    Nota de Arquitetura:
    Mantemos o OneToOneField explicitamente definido aqui, sobrescrevendo a
    ForeignKey padrão que o WeddingOwnedMixin forneceria.
    Isso é feito por dois motivos:
    1. Garantir a unicidade (ADR-003): Cada casamento deve ter exatamente UM orçamento
       mestre.
    2. Compatibilidade com o BaseViewSet: Ao herdar de WeddingOwnedMixin, o ViewSet
       continua identificando o modelo como "pertencente a um casamento" e aplica
       automaticamente os filtros de Multitenancy (Segurança por Design).
    """

    wedding = models.OneToOneField(
        "weddings.Wedding",
        on_delete=models.CASCADE,
        related_name="budget",
        verbose_name="Casamento",
    )
    total_estimated = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Orçamento Total Estimado",
    )
    notes = models.TextField(blank=True, verbose_name="Observações Gerais")

    class Meta:
        app_label = "finances"
        verbose_name = "Orçamento"
        verbose_name_plural = "Orçamentos"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Orçamento: {self.wedding} - R$ {self.total_estimated}"
