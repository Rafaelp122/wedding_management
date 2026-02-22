from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class PlannerOwnedMixin(models.Model):
    planner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(class)s_records",
    )

    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        # Filtra apenas campos declarados localmente que são FKs
        for field in self._meta.concrete_fields:
            if isinstance(field, models.ForeignKey):
                related_obj = getattr(self, field.name)
                # Verifica se o objeto relacionado também pertence a um casamento
                if related_obj and hasattr(related_obj, "wedding_id"):
                    if related_obj.wedding_id != self.wedding_id:
                        raise ValidationError(
                            {field.name: "Este recurso pertence a outro casamento."}
                        )


class WeddingOwnedMixin(models.Model):
    wedding = models.ForeignKey(
        "weddings.Wedding",
        on_delete=models.CASCADE,
        related_name="%(class)s_records",
    )

    class Meta:
        abstract = True

    def clean(self):
        """
        Garante que chaves estrangeiras pertençam ao mesmo casamento.
        Isso impede que um Item do Casamento A seja usado em uma Despesa do Casamento B.
        """
        super().clean()

        # Lógica genérica de validação de consistência
        for field in self._meta.get_fields():
            if isinstance(field, models.ForeignKey):
                related_obj = getattr(self, field.name)
                # Se o objeto relacionado também for 'WeddingOwned', os IDs devem bater
                if related_obj and hasattr(related_obj, "wedding_id"):
                    if related_obj.wedding_id != self.wedding_id:
                        raise ValidationError(
                            {field.name: "Este recurso pertence a outro casamento."}
                        )
