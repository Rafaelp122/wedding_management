import logging

from django.dispatch import receiver

from apps.events.signals import wedding_created
from apps.finances.services.budget_service import BudgetService


logger = logging.getLogger(__name__)


@receiver(wedding_created)
def auto_create_budget_for_wedding(sender, instance, **kwargs):
    """
    Escuta o app de Events. Quando um casamento nasce, cria o orçamento.
    Desacopla EventService de BudgetService.
    """
    logger.info(f"Finances: Criando orçamento automático para o Evento {instance.uuid}")

    # Como o sinal não tem o 'user', precisamos de um contexto.
    # Em cenários complexos, usaríamos o planner do evento.
    # O user.company do criador do evento é o que importa.
    # Para simplificar aqui, assumimos que o budget_service sabe lidar com o 'event'
    # mas o BudgetService.get_or_create_for_event precisa de um user.
    # Vamos adaptar o service para aceitar 'company' ou injetar um sistema de contexto.

    # Para este MVP, vamos garantir que o service possa ser chamado sem user
    # se tivermos a instância do evento (já validada no sinal).
    BudgetService.setup_initial_budget(instance)
