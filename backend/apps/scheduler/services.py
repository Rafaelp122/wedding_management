import logging

from django.db import transaction
from django.db.models import ProtectedError

from apps.core.exceptions import BusinessRuleViolation, DomainIntegrityError
from apps.scheduler.models import Event
from apps.weddings.models import Wedding


logger = logging.getLogger(__name__)


class EventService:
    """
    Camada de serviço para gestão de compromissos e calendário.
    Garante isolamento total (Multitenancy), auditoria e integridade de agendamento.
    """

    @staticmethod
    @transaction.atomic
    def create(user, data: dict) -> Event:
        logger.info(f"Iniciando criação de Evento para planner_id={user.id}")

        # 1. Resolução Segura de Dependências
        # O DRF pode enviar a instância já resolvida ou apenas o UUID. Tratamos ambos.
        wedding_input = data.pop("wedding", None)

        if isinstance(wedding_input, Wedding):
            wedding = wedding_input
        else:
            try:
                # Isolamento multitenant forçado na busca da dependência
                wedding = Wedding.objects.all().for_user(user).get(uuid=wedding_input)
            except Wedding.DoesNotExist as e:
                logger.warning(
                    f"Tentativa de agendamento em casamento inválido ou "
                    f"negado: {wedding_input} por planner_id={user.id}"
                )
                raise BusinessRuleViolation(
                    detail="Casamento não encontrado ou você não tem permissão para "
                    "acessá-lo.",
                    code="wedding_not_found_or_denied",
                ) from e

        # 2. Instanciação em Memória (NÃO salva no banco ainda)
        event = Event(planner=user, wedding=wedding, **data)

        # 3. Validação Estrita do Domínio
        # Aqui o Model garante que start_time < end_time e previne conflitos.
        event.full_clean()
        event.save()

        # TODO (RF12): Integração com Celery para agendar notificações de lembrete
        # NotificationService.schedule_event_reminder(event)

        logger.info(
            f"Evento criado com sucesso: uuid={event.uuid} no casamento "
            f"uuid={wedding.uuid}"
        )
        return event

    @staticmethod
    @transaction.atomic
    def update(instance: Event, user, data: dict) -> Event:
        logger.info(f"Atualizando Evento uuid={instance.uuid} por planner_id={user.id}")

        # Proteção contra sequestro de dados:
        # Impedimos que um evento seja movido para outro casamento/planner após criado.
        data.pop("wedding", None)
        data.pop("planner", None)

        for field, value in data.items():
            setattr(instance, field, value)

        # Validação estrita do Model para garantir que as novas datas não quebram regras
        instance.full_clean()
        instance.save()

        # TODO: Se as datas mudaram, reagendar a task no Celery

        logger.info(f"Evento uuid={instance.uuid} atualizado com sucesso.")
        return instance

    @staticmethod
    @transaction.atomic
    def delete(user, instance: Event) -> None:
        logger.info(
            f"Tentativa de deleção do Evento uuid={instance.uuid} por "
            f"planner_id={user.id}"
        )

        try:
            instance.delete()
            logger.warning(
                f"Evento uuid={instance.uuid} DESTRUÍDO por planner_id={user.id}"
            )

        except ProtectedError as e:
            logger.error(f"Falha de integridade ao deletar evento uuid={instance.uuid}")
            raise DomainIntegrityError(
                detail="Não é possível apagar este evento pois existem registros "
                "vinculados a ele.",
                code="event_protected_error",
            ) from e
