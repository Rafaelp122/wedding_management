import logging
from django.db import IntegrityError, transaction
from apps.core.exceptions import DomainIntegrityError
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
        1. Valida se o e-mail já existe.
        2. Cria a Empresa (Workspace) pragmático.
        3. Cria o Usuário vinculado a essa empresa.
        """
        logger.info(f"Iniciando registro de novo proprietário: {email}")

        # 1. Validação Preventiva
        if User.objects.filter(email=email).exists():
            raise DomainIntegrityError(
                detail="Este e-mail já está cadastrado em outra conta.",
                code="email_already_exists",
            )

        # 2. Criação da Empresa
        display_name = f"{first_name} {last_name}".strip() or email
        company = TenantService.create_company(display_name)

        # 3. Criação do Usuário com captura de erro de integridade (Race conditions)
        try:
            user = User.objects.create_user(
                email=email,
                password=password,
                company=company,
                first_name=first_name,
                last_name=last_name,
                is_active=True,
            )
        except IntegrityError as e:
            logger.error(f"Erro de integridade ao registrar usuário {email}: {e}")
            raise DomainIntegrityError(
                detail="Este e-mail já está cadastrado em outra conta.",
                code="email_already_exists",
            ) from e

        logger.info(
            f"Registro concluído com sucesso: user_uuid={user.uuid}, "
            f"company_slug={company.slug}"
        )
        return user
