import factory

from apps.events.models import Event, WeddingDetail
from apps.tenants.tests.factories import CompanyFactory


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    company = factory.SubFactory(CompanyFactory)
    name = factory.Faker("sentence", nb_words=3)
    event_type = Event.EventType.OTHER
    date = factory.Faker("date_between", start_date="+1d", end_date="+1y")
    location = factory.Faker("address")
    expected_guests = factory.Iterator([50, 100, 150, 200])
    status = Event.StatusChoices.IN_PROGRESS


class WeddingFactory(factory.django.DjangoModelFactory):
    """
    Fábrica de Casamentos (Independente para evitar erros de herança).
    """

    class Meta:
        model = Event

    company = factory.SubFactory(CompanyFactory)
    name = factory.Faker("sentence", nb_words=3)
    event_type = Event.EventType.WEDDING
    date = factory.Faker("date_between", start_date="+1d", end_date="+1y")
    location = factory.Faker("address")
    expected_guests = factory.Iterator([50, 100, 150, 200])
    status = Event.StatusChoices.IN_PROGRESS

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        # 1. Extrai nomes dos noivos antes de criar o Evento
        bride = kwargs.pop("bride_name", "Noiva Padrão")
        groom = kwargs.pop("groom_name", "Noivo Padrão")

        # 2. Cria o Evento base
        event = super()._create(model_class, *args, **kwargs)

        # 3. Cria o Detalhe
        WeddingDetail.objects.create(event=event, bride_name=bride, groom_name=groom)
        return event


class CompletedEventFactory(EventFactory):
    date = factory.Faker("past_date")
    status = Event.StatusChoices.COMPLETED
