# Em scheduler/models.py
# (Ou no models.py do seu app principal, se preferir)

from django.db import models
from django.conf import settings
from apps.weddings.models import Wedding # Ajuste este import para onde seu modelo Wedding está

class Schedule(models.Model):
    """
    Armazena um evento, tarefa ou prazo no calendário
    de um casamento específico.
    """
    # O VÍNCULO MAIS IMPORTANTE:
    wedding = models.ForeignKey(
        Wedding, 
        on_delete=models.CASCADE, 
        related_name="schedule_events", # Facilita buscas: wedding.schedule_events.all()
        verbose_name="Casamento"
    )
    
    title = models.CharField("Título do Evento", max_length=255)
    description = models.TextField("Descrição", blank=True, null=True)
    start_datetime = models.DateTimeField("Início do Evento")
    end_datetime = models.DateTimeField("Fim do Evento")

    planner = models.ForeignKey(
        settings.AUTH_USER_MODEL, # Ou seu modelo 'Planner'
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )

    class Meta:
        verbose_name = "Evento da Agenda"
        verbose_name_plural = "Eventos da Agenda"
        ordering = ['start_datetime'] # Ordena eventos por data de início

    def __str__(self):
        return self.title