from django.core.exceptions import ValidationError
from django.db import models


class WeddingOwnedMixin(models.Model):
    wedding = models.ForeignKey(
        "weddings.Wedding",
        on_delete=models.CASCADE,
        related_name="%(class)s_records",
    )

    class Meta:
        abstract = True

    def clean(self) -> None:
        """
        Valida a integridade do isolamento de dados (Multitenancy).
        Garante que chaves estrangeiras pertençam ao mesmo casamento E à mesma empresa.
        """
        super().clean()

        # 1. Blindagem Vertical: Garante que o recurso pertence à mesma empresa
        # que o casamento. Isso impede que o Casamento A da Empresa 1 seja
        # usado em um recurso da Empresa 2.
        if hasattr(self, "company_id") and self.wedding_id:
            if self.company_id != self.wedding.company_id:
                raise ValidationError(
                    {"wedding": "Este casamento pertence a outra organização."}
                )

        # 2. Lógica genérica de validação de consistência horizontal (entre casamentos)
        for field in self._meta.concrete_fields:
            if not isinstance(field, models.ForeignKey):
                continue
            if field.name == "wedding":
                continue

            fk_id = getattr(self, field.attname, None)
            if fk_id is None:
                continue

            if field.related_model is None or not hasattr(
                field.related_model, "wedding_id"
            ):
                continue

            related_obj = getattr(self, field.name)
            if related_obj and related_obj.wedding_id != self.wedding_id:
                raise ValidationError(
                    {field.name: "Este recurso pertence a outro casamento."}
                )
