"""
Modelo de Orçamento do domínio financeiro.

Responsabilidade: Gestão do orçamento mestre, definindo o teto financeiro global
do casamento.

Referência: RF03
"""

from decimal import Decimal
from typing import cast

from django.core.validators import MinValueValidator
from django.db import models

from apps.core.mixins import WeddingOwnedMixin
from apps.finances.managers import BudgetManager
from apps.tenants.models import TenantModel


class Budget(TenantModel, WeddingOwnedMixin):
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

    objects = BudgetManager()  # type: ignore[misc]

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
        indexes = [
            models.Index(fields=["company", "wedding"]),
        ]

    def __str__(self) -> str:
        return f"Orçamento: {self.wedding} - R$ {self.total_estimated}"

    @property
    def total_overall_spent(self) -> Decimal:
        """
        Retorna o total efetivamente pago em todas as categorias deste orçamento,
        somando apenas o ``amount`` das parcelas com status ``PAID``.

        .. warning::
           Esta property dispara uma query ``aggregate`` a cada acesso se não houver
           o atributo anotado ``_total_overall_spent``.
           Para múltiplas categorias, prefira
           ``Budget.objects.with_total_spent()`` que faz uma única
           query com ``annotate``.
        """
        val = getattr(self, "_total_overall_spent", None)
        if val is not None:
            return cast(Decimal, val)

        from django.db.models import Q, Sum

        from apps.finances.models.installment import Installment

        return self.categories.aggregate(
            total=Sum(
                "expenses__installments__amount",
                filter=Q(expenses__installments__status=Installment.StatusChoices.PAID),
            )
        )["total"] or Decimal("0.00")
