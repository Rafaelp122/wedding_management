import logging

from django.db.models.signals import post_save
from django.dispatch import Signal, receiver

from .models import Event


logger = logging.getLogger(__name__)

# Sinal customizado para quando um casamento é criado
wedding_created = Signal()


@receiver(post_save, sender=Event)
def handle_event_creation(sender, instance, created, **kwargs):
    """Encaminha para sinais específicos dependendo do tipo de evento."""
    if created and instance.event_type == Event.EventType.WEDDING:
        logger.info(
            f"Sinal: Disparando criação de workflow para Casamento {instance.uuid}"
        )
        wedding_created.send(sender=sender, instance=instance)
