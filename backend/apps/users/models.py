from typing import ClassVar

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MaxLengthValidator
from django.db import models


class CustomUserManager(BaseUserManager["User"]):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("O campo de E-mail é obrigatório")

        email = self.normalize_email(email)
        # Gera username automaticamente a partir do email se não fornecido
        if "username" not in extra_fields:
            extra_fields["username"] = email.split("@")[0]

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(
        max_length=255, unique=True, validators=[MaxLengthValidator(255)]
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: ClassVar[list] = ["username"]

    objects: ClassVar[CustomUserManager] = CustomUserManager()  # type: ignore[assignment]

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        ordering = ["-date_joined"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["username"]),
        ]

    def __str__(self):
        return self.email
