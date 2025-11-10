from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from apps.contracts.models import Contract
from .models import Item


# Cria automaticamente um contrato quando um novo item é salvo
@receiver(post_save, sender=Item)
def create_contract_for_new_item(sender, instance, created, **kwargs):
    # Executa apenas quando o item é criado pela primeira vez e tem fornecedor definido
    if created and instance.supplier:
        Contract.objects.create(
            item=instance,
            wedding=instance.wedding,
            supplier=instance.supplier,
            signature_date=timezone.now().date(),
            status="Pendente",
            description=f"Contrato para o item: {instance.name}",
        )
