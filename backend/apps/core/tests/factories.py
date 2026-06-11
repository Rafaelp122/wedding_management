"""
Factories mínimas para testes do app core.

Auto-contidas — sem dependência de SubFactory de outros apps.
"""

import factory

from apps.weddings.models import Wedding


class WeddingFactory(factory.django.DjangoModelFactory):
    """Factory local de Wedding para testes do core — sem cross-app SubFactory."""

    class Meta:
        model = Wedding

    company = factory.SubFactory("apps.tenants.tests.factories.CompanyFactory")
    groom_name = factory.Faker("first_name_male")
    bride_name = factory.Faker("first_name_female")
    date = factory.Faker("date_between", start_date="+30d", end_date="+365d")
    location = factory.Faker("address")
    expected_guests = factory.Iterator([50, 100, 150, 200])
    status = "IN_PROGRESS"
