from django.db import models
from django.db.models import DecimalField, ExpressionWrapper, F, Sum

from apps.supplier.models import Supplier
from apps.weddings.models import Wedding


class ItemQuerySet(models.QuerySet):
    def total_spent(self):
        """
        Calcula o custo total dos itens neste QuerySet.
        Retorna um Decimal ou 0.
        """
        total = self.aggregate(
            total=Sum(
                ExpressionWrapper(
                    F('unit_price') * F('quantity'),
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                )
            )
        )['total']
        return total or 0

    def category_expenses(self):
        """
        Agrupa os custos por categoria.
        Retorna um QuerySet de dicionários.
        """
        return self.values('category').annotate(
            total_cost=Sum(
                ExpressionWrapper(
                    F('unit_price') * F('quantity'),
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                )
            )
        ).order_by('-total_cost')


class Item(models.Model):

    CATEGORY_CHOICES = [
        ('LOCAL', 'Local '),
        ('BUFFET', 'Buffet'),
        ('DECOR', 'Decoração'),
        ('PHOTO_VIDEO', 'Fotografia e Vídeo'),
        ('ATTIRE', 'Vestuário'),
        ('MUSIC', 'Música/Entretenimento'),
        ('OTHERS', 'Outros'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    wedding = models.ForeignKey(
        Wedding, on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='OTHERS',
        verbose_name="Categoria"
    )

    objects = ItemQuerySet.as_manager()

    def __str__(self):
        return self.name

    @property
    def total_cost(self):
        return self.unit_price * self.quantity
