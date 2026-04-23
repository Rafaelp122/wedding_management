from typing import TypeVar

from django.db import models

from apps.core.types import AuthContextUser


_ModelT = TypeVar("_ModelT", bound=models.Model)


class BaseQuerySet(models.QuerySet[_ModelT]):
    def for_user(self, user: AuthContextUser) -> "BaseQuerySet[_ModelT]":
        """Filtra registos baseando-se na posse (Planner ou Wedding)."""
        # Escudo contra AnonymousUser
        if not user.is_authenticated:
            return self.none()

        from apps.core.mixins import PlannerOwnedMixin, WeddingOwnedMixin

        model = self.model

        if issubclass(model, WeddingOwnedMixin):
            return self.filter(wedding__planner=user)
        if issubclass(model, PlannerOwnedMixin):
            return self.filter(planner=user)

        return self


class BaseManager(models.Manager[_ModelT]):
    def get_queryset(self) -> BaseQuerySet[_ModelT]:
        return BaseQuerySet(self.model, using=self._db)

    def for_user(self, user: AuthContextUser) -> BaseQuerySet[_ModelT]:
        return self.get_queryset().for_user(user)
