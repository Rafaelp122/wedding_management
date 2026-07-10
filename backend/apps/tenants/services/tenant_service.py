import logging
import uuid as uuid_lib

from django.db import transaction
from django.utils.text import slugify

from apps.tenants.models import Company


logger = logging.getLogger(__name__)


class TenantService:
    """
    Serviço responsável pela gestão de tenants (Workspaces/Empresas).

    Centraliza a lógica de criação de workspaces e a inicialização de
    tenants para isolamento de dados no sistema.
    """

    @staticmethod
    @transaction.atomic
    def create_company(display_name: str, company_name: str = "") -> Company:
        """
        Cria uma Company com base no nome do usuário ou email.

        Gera um slug único e curto para evitar colisões e cria o tenant no
        banco de dados em uma transação atômica.

        Args:
            display_name: Nome de exibição do usuário proprietário.
            company_name: Nome opcional da empresa a ser criada.

        Returns:
            A instância de Company criada e persistida.
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
        Gera ou recupera o workspace de administração padrão do sistema.

        Utilizado para associar superusuários a um tenant administrativo do
        sistema, prevenindo erros de validação de tenant em ferramentas de
        gerenciamento global.

        Returns:
            A instância de Company representativa do workspace administrativo.
        """
        company, created = Company.objects.get_or_create(
            slug="admin-workspace", defaults={"name": "Workspace Administrativo"}
        )
        if created:
            logger.info("Workspace Administrativo criado via setup automático.")
        return company
