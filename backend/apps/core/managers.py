from typing import TypeVar
from uuid import UUID

from django.db import models

from apps.core.exceptions import ObjectNotFoundError
from apps.users.types import AuthContextUser


_ModelT = TypeVar("_ModelT", bound=models.Model)


class BaseQuerySet(models.QuerySet[_ModelT]):
    def for_user(self, user: AuthContextUser) -> "BaseQuerySet[_ModelT]":
        """
        Filtra registros de forma agnóstica baseando-se no Tenant (Company).

        Não importa Mixins diretamente para evitar dependências circulares.
        Usa flags configuradas nos modelos.
        """
        if not user.is_authenticated or not user.company:
            return self.none()

        model = self.model
        company = user.company

        # Verifica se o modelo é owned por Company (via flag no mixin/model)
        if getattr(model, "_is_company_owned", False):
            return self.filter(company=company)

        # Verifica se o modelo é owned por Event (via flag no mixin/model)
        if getattr(model, "_is_event_owned", False):
            return self.filter(event__company=company)

        # Fallback para modelos que ainda usam o campo planner (Legacy)
        if hasattr(model, "planner_id") and not hasattr(model, "company_id"):
            return self.filter(planner=user)

        return self

    def resolve(self, user: AuthContextUser, uuid: _ModelT | UUID | str) -> _ModelT:
        """Busca uma instância única garantindo a posse (Multitenancy)."""
        if isinstance(uuid, self.model):
            return uuid

        uuid_to_filter: UUID
        try:
            if isinstance(uuid, UUID):
                uuid_to_filter = uuid
            elif isinstance(uuid, str):
                uuid_to_filter = UUID(uuid)
            else:
                raise ValueError("Formato de UUID inválido")
        except (ValueError, TypeError) as e:
            raise ObjectNotFoundError(
                detail=f"Identificador inválido para {self.model._meta.verbose_name}.",
                code="invalid_uuid_format",
            ) from e

        instance = self.for_user(user).filter(uuid=uuid_to_filter).first()

        if not instance:
            label = self.model._meta.verbose_name or "Recurso"
            raise ObjectNotFoundError(
                detail=f"{label} não encontrado ou acesso negado.",
                code=f"{self.model._meta.model_name}_not_found_or_denied",
            )

        return instance


class BaseManager(models.Manager[_ModelT]):
    def get_queryset(self) -> BaseQuerySet[_ModelT]:
        return BaseQuerySet(self.model, using=self._db)

    def for_user(self, user: AuthContextUser) -> BaseQuerySet[_ModelT]:
        return self.get_queryset().for_user(user)

    def resolve(self, user: AuthContextUser, uuid: _ModelT | UUID | str) -> _ModelT:
        return self.get_queryset().resolve(user, uuid)
