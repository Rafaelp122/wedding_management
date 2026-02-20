from django.core.exceptions import ValidationError
from django.db import transaction

from apps.scheduler.models import Event
from apps.weddings.models import Wedding


class EventService:
    """
    Camada de serviço para gestão de compromissos e calendário.
    Garante isolamento total e integridade de agendamento (RF12).
    """

    @staticmethod
    @transaction.atomic
    def create(user, data: dict) -> Event:
        """
        Cria um evento vinculado a um casamento do Planner.
        """
        # 1. Recuperamos o casamento garantindo que ele pertence ao Planner.
        # O 'data' deve conter o 'wedding' (UUID ou ID vindo do Serializer).
        wedding_uuid = data.get("wedding")

        try:
            # Usamos o manager com o filtro de segurança que criamos.
            wedding = Wedding.objects.all().for_user(user).get(uuid=wedding_uuid)
        except Wedding.DoesNotExist:
            raise ValidationError({
                "wedding": "Casamento não encontrado ou acesso negado."
            }) from Wedding.DoesNotExist

        # 2. Injetamos as instâncias de posse
        data["planner"] = user
        data["wedding"] = wedding

        # 3. Criação direta
        event = Event.objects.create(**data)

        # RF12: Se houver lógica de disparar agendamento de lembretes no Celery,
        # o lugar de chamar a task é aqui, após o commit.
        return event

    @staticmethod
    @transaction.atomic
    def update(instance: Event, user, data: dict) -> Event:
        """
        Atualiza um evento protegendo a integridade do multitenancy.
        """
        # Impedimos a troca do Casamento após a criação para evitar fraude.
        data.pop("wedding", None)
        data.pop("planner", None)

        for field, value in data.items():
            setattr(instance, field, value)

        # Dispara o .clean() do WeddingOwnedMixin para validar consistência.
        instance.full_clean()
        instance.save()
        return instance

    @staticmethod
    @transaction.atomic
    def delete(user, instance: Event) -> None:
        """
        Executa a deleção real (Hard Delete).
        """
        # Como o BaseViewSet já filtrou o objeto pelo dono,
        # o 'instance' recebido aqui já é garantidamente deste Planner.
        instance.delete()
