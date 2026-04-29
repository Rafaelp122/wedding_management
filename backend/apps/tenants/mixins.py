from django.db import models


class CompanyOwnedMixin(models.Model):
    """
    Mixin para Multitenancy B2B.
    Vincula o registro a uma Empresa (Tenant).
    """

    company = models.ForeignKey(
        "tenants.Company",
        on_delete=models.CASCADE,
        related_name="%(class)s_records",
        verbose_name="Empresa",
    )

    # Flag para o BaseManager identificar a necessidade de filtro
    _is_company_owned = True

    class Meta:
        abstract = True
