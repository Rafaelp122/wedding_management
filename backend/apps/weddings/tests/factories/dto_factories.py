from datetime import date

import factory

from apps.weddings.dto import WeddingDTO


class WeddingDTOFactory(factory.Factory):
    """Fábrica para gerar DTOs de Wedding em memória."""

    class Meta:
        model = WeddingDTO

    planner_id = factory.Faker("uuid4")
    groom_name = factory.Faker("name_male")
    bride_name = factory.Faker("name_female")
    date = factory.LazyFunction(lambda: date(2026, 12, 31))
    location = factory.Faker("address")
    expected_guests = factory.Iterator([50, 100, 250])
    status = "IN_PROGRESS"
