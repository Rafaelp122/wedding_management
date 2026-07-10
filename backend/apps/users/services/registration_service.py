import logging

from django.contrib.auth.password_validation import validate_password
from django.db import IntegrityError, transaction

from apps.core.exceptions import DomainIntegrityError
from apps.tenants.services.tenant_service import TenantService
from apps.users.models import User


logger = logging.getLogger(__name__)


class RegistrationService:
    """
    Serviço de orquestração para registro de novos usuários e empresas.

    Assegura que o fluxo de cadastro e a criação do par Usuário-Empresa
    sejam executados de forma atômica no banco de dados.
    """

    @staticmethod
    @transaction.atomic
    def register_new_owner(
        email: str,
        password: str,
        first_name: str = "",
        last_name: str = "",
        company_name: str = "",
    ) -> User:
        """
        Realiza o onboarding completo de um novo proprietário (Owner).

        Cria a conta do usuário e a empresa correspondente em uma transação
        atômica, realizando validações de senha e de unicidade do e-mail.

        Args:
            email: E-mail do novo usuário. Deve ser único.
            password: Senha em formato texto puro a ser validada e criptografada.
            first_name: Primeiro nome do usuário.
            last_name: Sobrenome do usuário.
            company_name: Nome opcional da empresa a ser criada.

        Returns:
            Instância do usuário (User) recém-criado e associado à empresa.

        Raises:
            ValidationError: Se a senha não atender aos requisitos de segurança.
            DomainIntegrityError: Se o e-mail já estiver cadastrado no sistema.
        """
        logger.info(f"Iniciando registro de novo proprietário: {email}")

        # Validação de senha preventiva antes de persistir dados no banco.
        validate_password(password)

        # Evita prosseguir com a criação da empresa se o e-mail já existir.
        if User.objects.filter(email=email).exists():
            raise DomainIntegrityError(
                detail="Este e-mail já está cadastrado em outra conta.",
                code="email_already_exists",
            )

        # Cria a empresa associada ao novo usuário.
        display_name = f"{first_name} {last_name}".strip() or email
        company = TenantService.create_company(display_name, company_name=company_name)

        # Cria o usuário. Captura erro de concorrência se o e-mail for registrado
        # concorrentemente.
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
            logger.exception(f"Erro de integridade ao registrar usuário {email}")
            raise DomainIntegrityError(
                detail="Este e-mail já está cadastrado em outra conta.",
                code="email_already_exists",
            ) from e

        logger.info(
            f"Registro concluído com sucesso: user_uuid={user.uuid}, "
            f"company_slug={company.slug}"
        )
        return user
