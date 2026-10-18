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

    Regra de Negócio:
        BR-U01 (docs/architecture/domains/users-domain.md)
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
        """Realiza o onboarding completo de um novo proprietário (Owner).

        Regra de Negócio: [BR-U01](docs/architecture/domains/users-domain.md)
        Efeitos Colaterais: Cria atomicamente a empresa e o usuário proprietário; agenda envio de verificação pós-commit.

        Raises:
            ValidationError: Se a senha fornecida não atender aos critérios de segurança.
            DomainIntegrityError: Se o e-mail já estiver cadastrado no sistema.
        """
        logger.info(f"Iniciando registro de novo proprietário: {email}")

        # Validação de senha preventiva antes de persistir dados no banco.
        validate_password(password)

        # Evita prosseguir com a criação da empresa se o e-mail já existir.
        if User.objects.filter(email=email).exists():
            raise DomainIntegrityError(
                detail=f"Este e-mail já está cadastrado em outra conta: '{email}'.",
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
                is_active=False,
                is_email_verified=False,
            )
            from apps.users.services.email_verification_service import (
                EmailVerificationService,
            )

            transaction.on_commit(
                lambda: EmailVerificationService.send_verification_email(user),
                robust=True,
            )
        except IntegrityError as e:
            logger.exception(f"Erro de integridade ao registrar usuário {email}")
            raise DomainIntegrityError(
                detail=f"Este e-mail já está cadastrado em outra conta: '{email}'.",
                code="email_already_exists",
            ) from e

        logger.info(
            f"Registro concluído com sucesso: user_uuid={user.uuid}, "
            f"company_slug={company.slug}"
        )
        return user
