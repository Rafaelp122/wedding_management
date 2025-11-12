from django.db import models

from apps.core.models import BaseModel
from apps.users.models import User
from apps.weddings.models import Wedding

# Tipos de evento possíveis no calendário
EVENT_TYPE_CHOICES = (
    ("reuniao", "Reunião"),
    ("pagamento", "Pagamento"),
    ("visita", "Visita Técnica"),
    ("degustacao", "Degustação"),
    ("outro", "Outro"),
)


class Event(BaseModel):
    """Modelo que representa um evento/compromisso no calendário."""

    # Casamento ao qual o evento está vinculado (opcional)
    wedding = models.ForeignKey(
        Wedding,
        on_delete=models.CASCADE,
        related_name="events",
        null=True,
        blank=True,
    )

    # Usuário responsável (planner)
    planner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="events"
    )

    # Informações principais do evento
    title = models.CharField(max_length=255, verbose_name="Título")
    location = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Local"
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="Descrição"
    )
    event_type = models.CharField(
        max_length=50,
        choices=EVENT_TYPE_CHOICES,
        default="outro",
        verbose_name="Tipo de Evento",
    )

    # Datas e horários do evento
    start_time = models.DateTimeField(verbose_name="Início do Evento")
    end_time = models.DateTimeField(
        verbose_name="Fim do Evento",
        null=True,
        blank=True
    )

    def __str__(self):
        # Exibe o título do evento no admin e nas representações de texto
        return self.title
