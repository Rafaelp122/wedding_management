from django.db import models
from apps.users.models import Fornecedor
from apps.budget.models import Orcamento


class Item(models.Model):
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True)
    quantidade = models.IntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    orcamento = models.ForeignKey(Orcamento, on_delete=models.CASCADE)
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome
