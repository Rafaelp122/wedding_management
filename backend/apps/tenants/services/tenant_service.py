import logging
import uuid as uuid_lib

from django.db import transaction
from django.utils.text import slugify

from apps.tenants.models import Company


logger = logging.getLogger(__name__)


class TenantService:
    """Serviço responsável pela gestão de tenants (Workspaces/Empresas)."""

    @staticmethod
    @transaction.atomic
    def create_company(display_name: str, company_name: str = "") -> Company:
        """
        Cria uma Company com base no nome do usuário ou email.
        Se company_name for fornecido, usa-o diretamente como nome da empresa.
        Retorna a instância da empresa salva.
        """
        name = company_name.strip() if company_name else f"Workspace de {display_name}"

        # Geramos um slug único e curto para evitar colisões
        base_slug = slugify(display_name)[:40]
        unique_slug = f"{base_slug}-{str(uuid_lib.uuid4())[:8]}"

        company = Company.objects.create(name=name, slug=unique_slug, is_active=True)
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
