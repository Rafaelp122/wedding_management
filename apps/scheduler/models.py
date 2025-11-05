from django.db import models
from apps.weddings.models import Wedding
from apps.users.models import User

EVENT_TYPE_CHOICES = (
    ("reuniao", "Reunião"),
    ("pagamento", "Pagamento"),
    ("visita", "Visita Técnica"),
    ("degustacao", "Degustação"),
    ("outro", "Outro"),
)


class Event(models.Model):
    """
    Este é o modelo de Evento/Compromisso para o calendário.
    """

    # Relação com o Casamento (opcional, um evento pode ser geral)
    wedding = models.ForeignKey(
        Wedding,
        on_delete=models.CASCADE,
        related_name="events",
        null=True,  # Permite eventos que não são de um casamento específico
        blank=True,
    )

    # Relação com o Planner (para sabermos quem é o dono)
    planner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="events")

    # Campos do seu formulário original
    title = models.CharField(max_length=255, verbose_name="Título")
    location = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Local"
    )
    description = models.TextField(null=True, blank=True, verbose_name="Descrição")
    event_type = models.CharField(
        max_length=50,
        choices=EVENT_TYPE_CHOICES,
        default="outro",
        verbose_name="Tipo de Evento",
    )

    # Campos de data/hora
    start_time = models.DateTimeField(verbose_name="Início do Evento")
    end_time = models.DateTimeField(verbose_name="Fim do Evento", null=True, blank=True)

    def __str__(self):
        return self.title
