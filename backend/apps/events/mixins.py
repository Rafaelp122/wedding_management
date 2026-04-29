from django.core.exceptions import ValidationError
from django.db import models


class EventOwnedMixin(models.Model):
    """
    Mixin para recursos que pertencem a um Evento específico.
    Garante integridade referencial dentro do mesmo evento.
    """

    event = models.ForeignKey(
        "events.Event",
        on_delete=models.CASCADE,
        related_name="%(class)s_records",
    )

    # Flag para o BaseManager identificar a necessidade de filtro
    _is_event_owned = True

    class Meta:
        abstract = True

    def clean(self) -> None:
        super().clean()
        for field in self._meta.concrete_fields:
            if isinstance(field, models.ForeignKey):
                related_obj = getattr(self, field.name)
                if related_obj and hasattr(related_obj, "event_id"):
                    if related_obj.event_id != self.event_id:
                        raise ValidationError(
                            {field.name: "Este recurso pertence a outro evento."}
                        )
