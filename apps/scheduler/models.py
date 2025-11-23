from django.db import models

from apps.users.models import User
from apps.weddings.models import Wedding

from .querysets import EventQuerySet


class Event(models.Model):
    """Modelo que representa um evento/compromisso no calendário."""

    class TypeChoices(models.TextChoices):
        """Tipos de eventos disponíveis no calendário."""

        MEETING = "reuniao", "Reunião"
        PAYMENT = "pagamento", "Pagamento"
        VISIT = "visita", "Visita Técnica"
        TASTING = "degustacao", "Degustação"
        OTHER = "outro", "Outro"

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
        User, on_delete=models.CASCADE, related_name="events"
    )

    # Informações principais do evento
    title = models.CharField(max_length=255, verbose_name="Título")
    location = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Local"
    )
    description = models.TextField(
        null=True, blank=True, verbose_name="Descrição"
    )
    event_type = models.CharField(
        max_length=50,
        choices=TypeChoices.choices,
        default=TypeChoices.OTHER,
        verbose_name="Tipo de Evento",
    )

    # Datas e horários do evento
    start_time = models.DateTimeField(verbose_name="Início do Evento")
    end_time = models.DateTimeField(
        verbose_name="Fim do Evento", null=True, blank=True
    )

    # QuerySet customizado
    objects = EventQuerySet.as_manager()

    def __str__(self):
        # Exibe o título do evento no admin e nas representações de texto
        return self.title
