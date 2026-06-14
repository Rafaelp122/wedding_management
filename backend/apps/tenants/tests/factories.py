import uuid

import factory

from apps.tenants.models import Company


class CompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Company

    name = factory.Faker("company")
    slug = factory.LazyFunction(lambda: f"company-{uuid.uuid4().hex[:8]}")
    is_active = True
