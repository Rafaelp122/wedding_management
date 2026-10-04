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
        """
        Cria e inicializa uma nova empresa (tenant) no banco de dados.

        Gera um slug único a partir do nome de exibição e persiste a empresa
        em uma transação atômica.

        Efeitos Colaterais:
            - Persiste uma nova instância de Company no banco de dados.

        Args:
            display_name: Nome de exibição base para compor o título e slug do workspace.
            company_name: Nome customizado opcional da empresa a ser criada.

        Returns:
            Instância de Company criada e persistida.
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
        """
        Recupera ou provisiona o workspace administrativo global do sistema.

        Efeitos Colaterais:
            - Persiste a Company com slug 'admin-workspace' caso ainda não exista.

        Returns:
            Instância de Company correspondente ao workspace administrativo.
        """
        company, created = Company.objects.get_or_create(
            slug="admin-workspace", defaults={"name": "Workspace Administrativo"}
        )
        if created:
            logger.info("Workspace Administrativo criado via setup automático.")
        return company
