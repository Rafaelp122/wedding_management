from django.conf import settings
from django.db import models


class PlannerOwnedMixin(models.Model):
    """
    DEPRECATED: Use CompanyOwnedMixin em apps.tenants.mixins (ADR-016).
    Mantido temporariamente para compatibilidade durante o refactor.
    """

    planner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(class)s_deprecated_records",
    )

    class Meta:
        abstract = True
