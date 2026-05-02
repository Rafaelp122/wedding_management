import logging

from django.db import transaction

from apps.tenants.services.tenant_service import TenantService
from apps.users.models import User


logger = logging.getLogger(__name__)


class RegistrationService:
    """
    Serviço de orquestração para registro de novos usuários e empresas.
    Assegura que a criação do par Usuário-Empresa seja atômica.
    """

    @staticmethod
    @transaction.atomic
    def register_new_owner(
        email: str, password: str, first_name: str = "", last_name: str = ""
    ) -> User:
        """
        Realiza o onboarding completo de um novo profissional (Owner).
        1. Cria a Empresa (Workspace) pragmático.
        2. Cria o Usuário já vinculado a essa empresa.
        """
        logger.info(f"Iniciando registro de novo proprietário: {email}")

        # 1. Criação da Empresa (Lógica delegada ao domínio Tenant)
        display_name = f"{first_name} {last_name}".strip() or email
        company = TenantService.create_company(display_name)

        # 2. Criação do Usuário (Lógica delegada ao domínio User)
        # O CustomUserManager será usado aqui, garantindo o hash da senha
        user = User.objects.create_user(
            email=email,
            password=password,
            company=company,
            first_name=first_name,
            last_name=last_name,
            is_active=True,  # Usuário já nasce ativo no MVP
        )

        logger.info(
            f"Registro concluído com sucesso: user_uuid={user.uuid}, "
            f"company_slug={company.slug}"
        )
        return user
