"""Módulo de modelos de usuário customizado.

Define o modelo User personalizado usando email como identificador único
e o CustomUserManager para gerenciar a criação de usuários e superusuários.
"""

from typing import Any, cast

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    """Manager customizado para o modelo User.

    Gerencia a criação de usuários regulares e superusuários,
    usando email como campo de autenticação ao invés de username.

    Novos usuários regulares são criados inativos (is_active=False) por padrão,
    implementando um fluxo de ativação via email ou processo administrativo.
    Superusuários sempre são criados ativos com permissões totais.
    """

    def _create_user(
        self, email: str, password: str | None, **extra_fields: Any
    ) -> "User":
        """Método interno para criar e salvar um usuário com email e senha.

        Args:
            email (str): Endereço de email do usuário (obrigatório).
            password (str): Senha do usuário.
            **extra_fields: Campos adicionais para o modelo User.

        Returns:
            User: Instância do usuário criado.

        Raises:
            ValueError: Se o email não for fornecido.
        """
        if not email:
            raise ValueError("O e-mail é obrigatório.")
        email = self.normalize_email(email)
        user = cast("User", self.model(email=email, **extra_fields))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(
        self, email: str, password: str | None = None, **extra_fields: Any
    ) -> "User":
        """Cria e salva um usuário regular com email e senha.

        Por padrão, cria usuários com is_active=False, exigindo ativação
        via email ou processo administrativo.

        Args:
            email (str): Endereço de email do usuário.
            password (str, optional): Senha do usuário.
            **extra_fields: Campos adicionais do modelo User.

        Returns:
            User: Instância do usuário criado.
        """
        extra_fields.setdefault(
            "is_active", False
        )  # Só faça isso se tiver o fluxo de ativação pronto!
        return self._create_user(email, password, **extra_fields)

    def create_superuser(
        self, email: str, password: str | None = None, **extra_fields: Any
    ) -> "User":
        """Cria e salva um superusuário com permissões administrativas.

        Força is_staff=True, is_superuser=True e is_active=True para garantir
        acesso total ao sistema.

        Args:
            email (str): Endereço de email do superusuário.
            password (str, optional): Senha do superusuário.
            **extra_fields: Campos adicionais do modelo User.

        Returns:
            User: Instância do superusuário criado.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("first_name") is None:
            extra_fields["first_name"] = "Admin"
        if extra_fields.get("last_name") is None:
            extra_fields["last_name"] = "Sistema"

        # O Django já valida isso, mas manter o check simples não dói
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("E-mail", unique=True, max_length=255)

    # NOVOS CAMPOS EXPLÍCITOS
    first_name = models.CharField("Primeiro Nome", max_length=150)
    last_name = models.CharField("Sobrenome", max_length=150)

    is_staff = models.BooleanField("Status da Equipe", default=False)
    is_active = models.BooleanField("Ativo", default=False)
    date_joined = models.DateTimeField("Data de Cadastro", default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    # O comando createsuperuser agora pedirá os dois nomes
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        ordering = ["-date_joined"]

    def __str__(self) -> str:
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self) -> str:
        """Retorna o nome completo."""
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self) -> str:
        """Retorna apenas o primeiro nome."""
        return self.first_name
