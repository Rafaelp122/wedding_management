import logging

from django.db import transaction
from django.utils.text import slugify

from apps.tenants.models import Company


logger = logging.getLogger(__name__)


class TenantService:
    """Serviço responsável pela gestão de tenants e vinculação de usuários."""

    @staticmethod
    def create_organization_for_user(user) -> Company:
        """
        Cria uma Company para o usuário baseado em seu perfil.
        Garante a atomicidade da operação.
        """
        if user.company:
            return user.company

        full_name = user.get_full_name()
        display_name = full_name if full_name else user.email

        if user.is_superuser:
            name = "Workspace Administrativo"
            base_slug = "admin-workspace"
        else:
            name = f"Workspace de {display_name}"
            base_slug = slugify(display_name)[:40]

        # Garante unicidade com o UUID do usuário
        unique_slug = f"{base_slug}-{str(user.uuid)[:8]}"

        with transaction.atomic():
            company, created = Company.objects.get_or_create(
                slug=unique_slug if not user.is_superuser else base_slug,
                defaults={"name": name},
            )

            # Vinculação via update para evitar trigger de signals de save recursivos
            from apps.users.models import User

            User.objects.filter(pk=user.pk).update(company=company)

            # Atualiza a instância em memória para uso imediato (ex: em testes)
            user.company = company

            if created:
                logger.info(
                    f"Tenant '{company.slug}' criado para o usuário {user.email}"
                )

            return company
