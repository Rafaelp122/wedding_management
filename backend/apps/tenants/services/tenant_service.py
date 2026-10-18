import logging
import uuid as uuid_lib

from django.db import transaction
from django.utils.text import slugify

from apps.tenants.models import Company


logger = logging.getLogger(__name__)


class TenantService:
    """
    Camada de serviço responsável pelo ciclo de vida de tenants e workspaces.

    Regra de Negócio:
        BR-T01 (docs/architecture/domains/tenants-domain.md)
    Decisão Arquitetural:
        ADR-019 (docs/architecture/adr/019-tenant-validation-service-layer.md)
    """

    @staticmethod
    @transaction.atomic
    def create_company(display_name: str, company_name: str = "") -> Company:
        """Cria e inicializa uma nova empresa (tenant) no banco de dados.

        Regra de Negócio: [BR-T01](docs/architecture/domains/tenants-domain.md)
        Efeitos Colaterais: Persiste uma nova instância de Company no banco de dados.
        """
        name = company_name.strip() if company_name else f"Workspace de {display_name}"

        # Gera um slug único concatenando um uuid curto para evitar colisões.
        base_slug = slugify(display_name)[:40]
        unique_slug = f"{base_slug}-{str(uuid_lib.uuid4())[:8]}"

        company = Company.objects.create(name=name, slug=unique_slug, is_active=True)
        logger.info(f"Tenant pragmático criado: {company.slug}")
        return company

    @staticmethod
    @transaction.atomic
    def get_or_create_admin_workspace() -> Company:
        """Recupera ou provisiona o workspace administrativo global do sistema.

        Decisão Arquitetural: [ADR-019](docs/architecture/adr/019-tenant-validation-service-layer.md)
        Efeitos Colaterais: Persiste a Company com slug 'admin-workspace' caso ainda não exista.
        """
        company, created = Company.objects.get_or_create(
            slug="admin-workspace", defaults={"name": "Workspace Administrativo"}
        )
        if created:
            logger.info("Workspace Administrativo criado via setup automático.")
        return company
