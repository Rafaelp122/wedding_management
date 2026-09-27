"""
Entidades e regras de integridade do domínio de clientes e contatos.
"""

from __future__ import annotations

from typing import Any

from django.core.exceptions import ValidationError
from django.db import models

from apps.clients.managers import ClientManager
from apps.tenants.models import TenantModel


class Client(TenantModel):
    """
    Representa uma pessoa física cadastrada como cliente ou contato (ADR-030).

    Pode participar de um ou múltiplos casamentos sob diferentes papéis (noiva,
    noivo, contratante financeiro, representante legal, etc.).
    """

    objects: ClientManager = ClientManager()  # type: ignore[misc]

    name = models.CharField("Nome Completo", max_length=255)
    cpf = models.CharField("CPF", max_length=14, blank=True, default="")
    email = models.EmailField("E-mail", blank=True, default="")
    phone = models.CharField("Telefone", max_length=20, blank=True, default="")
    notes = models.TextField("Observações", blank=True, default="")

    class Meta:
        db_table = "clients"
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["company", "name"]),
            models.Index(fields=["company", "cpf"]),
            models.Index(fields=["company", "email"]),
        ]

    def __str__(self) -> str:
        if self.cpf:
            return f"{self.name} ({self.cpf})"
        return self.name

    def clean_fields(self, exclude: Any = None) -> None:
        """Sanitiza campos antes da validação estrutural do Django."""
        if self.name:
            self.name = self.name.strip()
        if self.email:
            self.email = self.email.strip().lower()
        if self.phone:
            self.phone = self.phone.strip()
        if self.cpf:
            self.cpf = self.cpf.strip()
        super().clean_fields(exclude=exclude)

    def clean(self) -> None:
        """
        Guardião de integridade e sanitização de dados do cliente (ADR-030).
        """
        super().clean()

        if self.name:
            self.name = self.name.strip()
        if not self.name:
            raise ValidationError({"name": "O nome do cliente é obrigatório."})

        if self.email:
            self.email = self.email.strip().lower()

        if self.phone:
            self.phone = self.phone.strip()

        if self.cpf:
            self.cpf = self.cpf.strip()
            if len(self.cpf) > 14:
                raise ValidationError(
                    {"cpf": "O CPF não pode ter mais de 14 caracteres."}
                )

    def update_contact_info(
        self,
        *,
        name: str | None = None,
        cpf: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        notes: str | None = None,
    ) -> None:
        """
        Atualiza dados cadastrais e de contato do cliente.

        Args:
            name: Nome completo atualizado.
            cpf: CPF atualizado.
            email: E-mail de contato atualizado.
            phone: Telefone com DDD atualizado.
            notes: Observações cadastrais atualizadas.
        """
        if name is not None:
            self.name = name
        if cpf is not None:
            self.cpf = cpf
        if email is not None:
            self.email = email
        if phone is not None:
            self.phone = phone
        if notes is not None:
            self.notes = notes
