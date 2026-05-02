import factory

from apps.tenants.models import Company


class CompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Company

    name = factory.Faker("company")
    slug = factory.Sequence(lambda n: f"company-{n}")
    is_active = True
