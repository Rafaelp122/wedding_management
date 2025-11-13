from django.db import models

from apps.core.models import BaseModel


class ContactInquiry(BaseModel):
    name = models.CharField("Nome", max_length=100)
    email = models.EmailField("E-mail")
    message = models.TextField("Mensagem")

    # Campo para controlo no Admin
    read = models.BooleanField("Lido", default=False)

    class Meta:
        verbose_name = "Mensagem de Contato"
        verbose_name_plural = "Mensagens de Contato"
        # A ordenação por 'created_at' funciona porque vem do BaseModel
        ordering = ('-created_at',)

    def __str__(self):
        return f"Mensagem de {self.name} ({self.email})"
