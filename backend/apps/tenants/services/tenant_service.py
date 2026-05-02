import logging

from django.db import transaction
from django.utils.text import slugify

from apps.tenants.models import Company


logger = logging.getLogger(__name__)


class TenantService:
    """Serviço responsável pela gestão de tenants (Workspaces/Empresas)."""

    @staticmethod
    @transaction.atomic
    def create_company(display_name: str) -> Company:
        """
        Cria uma Company com base no nome do usuário ou email.
        Retorna a instância da empresa salva.
        """
        company_name = f"Workspace de {display_name}"

        # Geramos um slug único e curto para evitar colisões
        import uuid as uuid_lib

        base_slug = slugify(display_name)[:40]
        unique_slug = f"{base_slug}-{str(uuid_lib.uuid4())[:8]}"

        company = Company.objects.create(
            name=company_name, slug=unique_slug, is_active=True
        )
        logger.info(f"Tenant pragmático criado: {company.slug}")
        return company

    @staticmethod
    @transaction.atomic
    def get_or_create_admin_workspace() -> Company:
        """Garante a existência do workspace administrativo para superusuários."""
        company, created = Company.objects.get_or_create(
            slug="admin-workspace", defaults={"name": "Workspace Administrativo"}
        )
        if created:
            logger.info("Workspace Administrativo criado via setup automático.")
        return company
