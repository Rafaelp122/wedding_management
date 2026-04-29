import logging

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.tenants.models import Company
from apps.users.models import User


logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_company(sender, instance, created, **kwargs):
    """
    SIGNAL: Tenant Silencioso (ADR-016).
    Toda vez que um usuário é criado, criamos uma Company padrão para ele
    e o vinculamos, garantindo que o sistema opere sempre em modo B2B.
    """
    if not created:
        return

    # Se o usuário já veio com empresa (ex: convite), não fazemos nada
    if instance.company_id:
        return

    logger.info(f"Criando Tenant Silencioso para o usuário: {instance.email}")

    try:
        with transaction.atomic():
            # Cria a empresa com o nome do usuário ou um nome padrão
            company_name = f"Agência de {instance.get_full_name() or instance.email}"
            company = Company.objects.create(name=company_name)

            # Vincula o usuário à empresa recém-criada
            instance.company = company
            instance.save(update_fields=["company"])

            logger.info(
                f"Empresa '{company.name}' vinculada ao usuário {instance.email}"
            )
    except Exception as e:
        logger.error(f"Erro ao criar empresa para o usuário {instance.email}: {e}")
        # Em produção, você poderia decidir se quer travar a criação do user ou não.
        # Aqui, como é um Tenant Silencioso mandatório, o erro é crítico.
