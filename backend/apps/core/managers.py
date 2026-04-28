from typing import TypeVar
from uuid import UUID

from django.db import models

from apps.core.exceptions import ObjectNotFoundError
from apps.core.types import AuthContextUser


_ModelT = TypeVar("_ModelT", bound=models.Model)


class BaseQuerySet(models.QuerySet[_ModelT]):
    def for_user(self, user: AuthContextUser) -> "BaseQuerySet[_ModelT]":
        """Filtra registos baseando-se na posse (Planner ou Wedding)."""
        if not user.is_authenticated:
            return self.none()

        from apps.core.mixins import PlannerOwnedMixin, WeddingOwnedMixin

        model = self.model

        if issubclass(model, WeddingOwnedMixin):
            return self.filter(wedding__planner=user)
        if issubclass(model, PlannerOwnedMixin):
            return self.filter(planner=user)

        return self

    def resolve(self, user: AuthContextUser, uuid: _ModelT | UUID | str) -> _ModelT:
        """
        RESOLVER: Busca uma instância única garantindo a posse (Multitenancy).

        ESTRATÉGIA DE USO (ADR-015):
        - Vem da URL (Path Param)? O Controller usa Model.objects.resolve(user, uuid).
        - Vem do JSON (Payload)? O Service usa Model.objects.resolve(user, uuid).

        Esta abordagem permite encadeamento para performance, ex:
        >>> Budget.objects.select_related('wedding').resolve(user, uuid)
        """
        # 1. Idempotência: se já for a instância, apenas retorna
        if isinstance(uuid, self.model):
            return uuid

        # 2. Validação de formato de UUID (Previne Erro 500 no Banco)
        uuid_to_filter: UUID
        try:
            if isinstance(uuid, UUID):
                uuid_to_filter = uuid
            elif isinstance(uuid, str):
                uuid_to_filter = UUID(uuid)
            else:
                # Caso extremo onde não é str nem UUID nem Instância
                raise ValueError("Formato de UUID inválido")
        except (ValueError, TypeError) as e:
            raise ObjectNotFoundError(
                detail=f"Identificador inválido para {self.model._meta.verbose_name}.",
                code="invalid_uuid_format",
            ) from e

        # 3. Busca com filtro de segurança (Reusa o for_user)
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
