from django.db import models

from apps.supplier.models import Supplier
from apps.weddings.models import Wedding

from .querysets import ItemQuerySet


class Item(models.Model):
    # Modelo que representa um item de orçamento vinculado a um casamento

    CATEGORY_CHOICES = [
        ("LOCAL", "Local"),
        ("BUFFET", "Buffet"),
        ("DECOR", "Decoração"),
        ("PHOTO_VIDEO", "Fotografia e Vídeo"),
        ("ATTIRE", "Vestuário"),
        ("MUSIC", "Música/Entretenimento"),
        ("OTHERS", "Outros"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Pendente"),
        ("IN_PROGRESS", "Em Andamento"),
        ("DONE", "Concluído"),
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
        Wedding,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="OTHERS",
        verbose_name="Categoria",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
        verbose_name="Status",
    )

    # Conecta o QuerySet personalizado
    objects = ItemQuerySet.as_manager()

    def __str__(self):
        # Exibe o nome do item no Django Admin e em representações de texto
        return self.name

    @property
    def total_cost(self):
        # Calcula o custo total do item (quantidade * preço unitário)
        return self.unit_price * self.quantity
