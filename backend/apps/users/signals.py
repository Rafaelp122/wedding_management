from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.tenants.services.tenant_service import TenantService

from .models import User


@receiver(post_save, sender=User)
def handle_user_tenant_creation(sender, instance, created, **kwargs):
    """
    Trigger silencioso para garantir que todo usuário tenha um tenant.
    Delega a lógica de negócio para o TenantService.
    """
    if created and not instance.company:
        # Delegamos a lógica de negócio para o serviço especializado
        TenantService.create_organization_for_user(instance)
