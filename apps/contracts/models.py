from django.db import models
from apps.users.models import Cerimonialista, Cliente
from apps.budget.models import Orcamento


class Contrato(models.Model):
    data_assinatura = models.DateField()
    validade = models.DateField(null=True, blank=True)
    descricao = models.TextField(blank=True)
    status = models.CharField(max_length=50, blank=True)
    cerimonialista = models.ForeignKey(Cerimonialista, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    orcamento = models.ForeignKey(Orcamento, on_delete=models.CASCADE)

    def __str__(self):
        return f'Contrato #{self.id}'
