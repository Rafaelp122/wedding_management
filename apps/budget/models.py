from django.db import models
from apps.users.models import Cerimonialista


class Orcamento(models.Model):
    estimativa_inicial = models.DecimalField(max_digits=10, decimal_places=2)
    valor_final = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=50, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    cerimonialista = models.ForeignKey(Cerimonialista, on_delete=models.CASCADE)

    def __str__(self):
        return f'Orçamento #{self.id}'