from django.db import models

from apps.core.models import BaseModel


class ContactInquiry(BaseModel):
    """
    Representa uma mensagem enviada através do formulário de contato.
    Armazena nome, email, mensagem e status de leitura.
    """
    name = models.CharField("Nome", max_length=100)
    email = models.EmailField("E-mail")
    message = models.TextField("Mensagem")

    # Campo para controle no Admin
    read = models.BooleanField("Lido", default=False)

    class Meta:
        verbose_name = "Mensagem de Contato"
        verbose_name_plural = "Mensagens de Contato"
        ordering = ("-created_at",)

    def __str__(self):
        return f"Mensagem de {self.name} ({self.email})"

    def mark_as_read(self):
        """Marca a mensagem como lida e salva."""
        if not self.read:
            self.read = True
            self.save(update_fields=["read"])
