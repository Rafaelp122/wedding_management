import factory

from apps.notifications.models import Notification, NotificationType
from apps.users.tests.factories import UserFactory


class NotificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Notification

    user = factory.SubFactory(UserFactory)
    company = factory.LazyAttribute(lambda o: o.user.company)
    title = factory.Faker("sentence", nb_words=4)
    message = factory.Faker("paragraph")
    type = NotificationType.GENERAL
    is_read = False
    link = ""
    read_at = None
