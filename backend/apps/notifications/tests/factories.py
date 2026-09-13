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
    target_type = ""
    target_id = None
    wedding_id = None
    is_read = False
    link = ""
    read_at = None

    @classmethod
    def _adjust_kwargs(cls, **kwargs: object) -> dict[str, object]:
        kwargs = super()._adjust_kwargs(**kwargs)
        if "company" in kwargs and "user" not in kwargs:
            kwargs["user"] = UserFactory(company=kwargs["company"])
        return kwargs
