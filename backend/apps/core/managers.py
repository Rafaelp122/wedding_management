from django.db import models


class BaseQuerySet(models.QuerySet):
    def for_user(self, user):
        """Filtra registos baseando-se na posse (Planner ou Wedding)."""
        # Escudo contra AnonymousUser (usado pelo drf-spectacular) ---
        if not user.is_authenticated:
            return self.none()

        model = self.model
        field_names = [f.name for f in model._meta.get_fields()]

        if "wedding" in field_names:
            return self.filter(wedding__planner=user)
        if "planner" in field_names:
            return self.filter(planner=user)
        return self


class BaseManager(models.Manager):
    def get_queryset(self):
        return BaseQuerySet(self.model, using=self._db)
