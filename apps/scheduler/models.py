from django.db import models
from apps.users.models import Cerimonialista
from apps.contracts.models import Contrato


class Agendamento(models.Model):
    titulo = models.CharField(max_length=255)
    descricao = models.TextField(blank=True)
    data_hora = models.DateTimeField()
    tipo = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=50, blank=True)
    cerimonialista = models.ForeignKey(Cerimonialista, on_delete=models.CASCADE)  
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo