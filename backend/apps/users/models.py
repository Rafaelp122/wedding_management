"""Módulo de modelos de usuário customizado.

Define o modelo User personalizado usando email como identificador único
e o CustomUserManager para gerenciar a criação de usuários e superusuários.
"""

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

    def _create_user(self, email, password, **extra_fields):
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
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
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

    def create_superuser(self, email, password=None, **extra_fields):
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

        # O Django já valida isso, mas manter o check simples não dói
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Modelo de usuário customizado usando email como identificador único.

    Implementa RF02 (Gestão de Permissões) com suporte a níveis de acesso:
    - Owner (is_staff=True, is_superuser=True): Acesso total
    - Editor (is_staff=True): Acesso ao admin sem super poderes
    - Viewer (is_staff=False): Acesso apenas via API

    Novos usuários regulares são criados com is_active=False por padrão,
    exigindo ativação manual. Superusuários são sempre criados ativos.

    O sistema usa email para autenticação (USERNAME_FIELD) ao invés do
    username tradicional do Django.

    Attributes:
        email (EmailField): Email único do usuário (usado para login).
        name (CharField): Nome completo do usuário (obrigatório).
        is_staff (BooleanField): Define se o usuário tem acesso ao admin.
        is_active (BooleanField): Define se o usuário está ativo no sistema.
        date_joined (DateTimeField): Data de cadastro do usuário.

    Usage:
        # Criar usuário regular (inativo por padrão)
        user = User.objects.create_user(
            email='usuario@example.com',
            name='João Silva',
            password='senha_segura'
        )

        # Criar superusuário (ativo automaticamente)
        admin = User.objects.create_superuser(
            email='admin@example.com',
            name='Admin Sistema',
            password='senha_admin'
        )
    """

    email = models.EmailField("E-mail", unique=True, max_length=255)
    name = models.CharField("Nome Completo", max_length=255)

    is_staff = models.BooleanField("Status da Equipe", default=False)
    is_active = models.BooleanField("Ativo", default=False)
    date_joined = models.DateTimeField("Data de Cadastro", default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    # O comando createsuperuser agora exigirá o nome, evitando registros fantasmas
    REQUIRED_FIELDS = ["name"]

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        ordering = ["-date_joined"]

    def __str__(self):
        """Retorna representação em string do usuário.

        Returns:
            str: Nome completo e email do usuário.
        """
        return f"{self.name} ({self.email})"

    def get_full_name(self):
        """Retorna o nome completo do usuário.

        Returns:
            str: Nome completo do usuário.
        """
        return self.name

    def get_short_name(self):
        """Retorna o primeiro nome do usuário ou email se o nome não existir.

        Returns:
            str: Primeiro nome do usuário ou email como fallback.
        """
        return self.name.split()[0] if self.name else self.email
