"""
Mixins reutilizáveis para views de contratos.
Seguindo o padrão de organização do app weddings.
"""

import logging
from typing import TYPE_CHECKING, Any, Dict

from django.http import HttpRequest
from django.shortcuts import get_object_or_404

from apps.contracts.constants import (
    EXTERNAL_CONTRACT_HASH,
    STATUS_CANCELED,
    STATUS_COMPLETED,
)
from apps.contracts.models import Contract
from apps.core.mixins.auth import OwnerRequiredMixin
from apps.core.mixins.responses import JsonResponseMixin

if TYPE_CHECKING:
    from apps.contracts.querysets import ContractQuerySet

logger = logging.getLogger(__name__)


# --- Mixins Independentes (Standalone) ---


class ContractOwnershipMixin(OwnerRequiredMixin):
    """
    Define model e owner_field_name para contratos.

    Este mixin especializa o OwnerRequiredMixin genérico para o modelo
    Contract, garantindo que apenas o cerimonialista dono do casamento
    possa acessar o contrato.

    Usage:
        class MyContractView(ContractOwnershipMixin, UpdateView):
            fields = ['description', 'status']
    """

    model = Contract
    owner_field_name = "item__wedding__planner"


class ContractQuerysetMixin:
    """
    Fine-Grained Mixin: Query Logic

    Responsável por construir querysets de Contract.
    Encapsula toda a lógica de filtragem e busca de contratos.

    Attributes:
        request: HttpRequest object (deve ser fornecido pela View).
    """

    request: HttpRequest

    def get_contracts_for_planner(self) -> "ContractQuerySet":
        """
        Retorna todos os contratos do cerimonialista logado.

        Returns:
            QuerySet filtrado e otimizado de Contract.
        """
        return Contract.objects.for_planner(self.request.user).with_related()

    def get_contracts_for_wedding(self, wedding_id: int) -> "ContractQuerySet":
        """
        Retorna contratos de um casamento específico.

        Args:
            wedding_id: ID do casamento.

        Returns:
            QuerySet filtrado de Contract.
        """
        from apps.weddings.models import Wedding

        wedding = get_object_or_404(Wedding, id=wedding_id, planner=self.request.user)

        return Contract.objects.for_wedding(wedding).with_related()


class ContractSignatureMixin:
    """
    Fine-Grained Mixin: Signature Logic

    Responsável pela lógica de assinatura de contratos.
    Extrai a lógica repetida de processamento de assinaturas.
    """

    def get_client_ip(self, request: HttpRequest) -> str:
        """
        Extrai o IP do cliente da request para auditoria.

        Args:
            request: HttpRequest object.

        Returns:
            String com o IP do cliente.
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    def process_contract_signature(
        self, contract: Contract, signature_b64: str, request: HttpRequest
    ) -> tuple[bool, str]:
        """
        Processa a assinatura de um contrato.

        Args:
            contract: Instância do Contract.
            signature_b64: Assinatura em base64.
            request: HttpRequest object.

        Returns:
            Tupla (sucesso: bool, mensagem: str).
        """
        if not signature_b64:
            return False, "Assinatura vazia."

        try:
            client_ip = self.get_client_ip(request)
            contract.process_signature(signature_b64, client_ip)
            return True, "Assinatura processada com sucesso."

        except ValueError as e:
            logger.warning(f"Erro de validação na assinatura: {e!s}")
            return False, f"Erro de validação: {e!s}"

        except RuntimeError as e:
            logger.error(f"Erro de runtime na assinatura: {e!s}")
            return False, f"Erro: {e!s}"

        except Exception as e:
            logger.exception("Erro inesperado ao processar assinatura")
            return False, f"Erro técnico: {e!s}"


class ContractUrlGeneratorMixin:
    """
    Fine-Grained Mixin: URL Generation Logic

    Responsável pela geração de URLs e links de assinatura.
    """

    request: HttpRequest

    def generate_signature_link(self, contract: Contract) -> Dict[str, Any]:
        """
        Gera o link de assinatura e informações do próximo signatário.

        Args:
            contract: Instância do Contract.

        Returns:
            Dicionário com link, status e próximo signatário.
        """
        try:
            link = self.request.build_absolute_uri(contract.get_absolute_url())
        except Exception as e:
            logger.error(f"Erro ao gerar URL: {e!s}")
            return {"link": f"ERRO NA URL: {e!s}"}

        next_signer_info = contract.get_next_signer_info()

        return {
            "link": link,
            "status": contract.status,
            "next_signer": next_signer_info["name"],
            "message": f"Próximo a assinar: {next_signer_info['name']}",
        }


class ContractEmailMixin:
    """
    Fine-Grained Mixin: Email Logic

    Responsável pelo envio de e-mails relacionados a contratos.
    """

    request: HttpRequest

    def send_signature_email(
        self, contract: Contract, recipient_email: str
    ) -> tuple[bool, str]:
        """
        Envia e-mail com link de assinatura.

        Args:
            contract: Instância do Contract.
            recipient_email: E-mail do destinatário.

        Returns:
            Tupla (sucesso: bool, mensagem: str).
        """
        from django.conf import settings
        from django.core.mail import send_mail

        try:
            link = self.request.build_absolute_uri(contract.get_absolute_url())

            subject = f"Assinatura Pendente: {contract.item.name}"
            message = f"""
Olá,

Um contrato requer sua assinatura digital no sistema Sim, Aceito.

Item: {contract.item.name}
Status: {contract.get_status_display()}

Acesse o link seguro abaixo para visualizar e assinar:
{link}

Atenciosamente,
Equipe Sim, Aceito.
            """

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [recipient_email],
                fail_silently=False,
            )

            return True, f"E-mail enviado com sucesso para {recipient_email}!"

        except Exception as e:
            logger.exception(f"Erro ao enviar e-mail para {recipient_email}")
            return False, f"Erro ao enviar e-mail: {e!s}"


class ContractActionsMixin:
    """
    Fine-Grained Mixin: Contract Actions

    Responsável por ações específicas em contratos usando querysets
    para validação e operações eficientes.
    """

    request: HttpRequest

    def cancel_contract(self, contract: Contract) -> tuple[bool, str]:
        """
        Cancela um contrato se possível.
        Usa queryset para validar se é cancelável.

        Args:
            contract: Instância do Contract.

        Returns:
            Tupla (sucesso: bool, mensagem: str).
        """
        # Usa queryset para verificar se é cancelável
        is_cancelable = Contract.objects.filter(pk=contract.pk).cancelable().exists()

        if not is_cancelable:
            return (False, "Não é possível cancelar um contrato concluído.")

        contract.status = STATUS_CANCELED
        contract.save()
        return True, "Contrato cancelado com sucesso."

    def update_contract_description(
        self, contract: Contract, new_description: str
    ) -> tuple[bool, str]:
        """
        Atualiza a descrição de um contrato editável.
        Usa queryset para verificar se é editável.

        Args:
            contract: Instância do Contract.
            new_description: Nova descrição do contrato.

        Returns:
            Tupla (sucesso: bool, mensagem: str).
        """
        # Usa queryset para verificar se é editável
        is_editable = Contract.objects.filter(pk=contract.pk).editable().exists()

        if not is_editable:
            return (
                False,
                "Não é possível editar um contrato que já foi "
                "enviado/assinado por outros.",
            )

        if not new_description:
            return False, "A descrição não pode estar vazia."

        contract.description = new_description
        contract.save()
        return True, "Termos atualizados com sucesso!"

    def upload_external_contract(
        self, contract: Contract, pdf_file
    ) -> tuple[bool, str]:
        """
        Faz upload de um contrato assinado externamente.

        Args:
            contract: Instância do Contract.
            pdf_file: Arquivo PDF enviado.

        Returns:
            Tupla (sucesso: bool, mensagem: str).
        """
        if not pdf_file:
            return False, "Nenhum arquivo enviado."

        if not pdf_file.name.endswith(".pdf"):
            return False, "Apenas arquivos PDF são permitidos."

        contract.external_pdf = pdf_file
        contract.status = STATUS_COMPLETED
        contract.integrity_hash = EXTERNAL_CONTRACT_HASH
        contract.save()

        return True, "Contrato externo anexado e finalizado!"


# --- Mixin de Composição (Facade Pattern) ---


class ContractManagementMixin(
    ContractQuerysetMixin,
    ContractSignatureMixin,
    ContractUrlGeneratorMixin,
    ContractEmailMixin,
    ContractActionsMixin,
    JsonResponseMixin,
):
    """
    Mixin de Composição (Composition Mixin) - Facade Pattern

    Este mixin atua como uma "fachada" que agrupa todos os mixins
    granulares de contratos em uma única interface conveniente.

    Composição Interna:
        - ContractQuerysetMixin: Query logic
        - ContractSignatureMixin: Signature processing
        - ContractUrlGeneratorMixin: URL generation
        - ContractEmailMixin: Email sending
        - ContractActionsMixin: Contract actions
        - JsonResponseMixin: JSON response helpers

    Requisitos da View que herda este mixin:
        - Atributos obrigatórios:
            * request: HttpRequest - Fornecido automaticamente

    Usage:
        class MyContractView(
            ContractOwnershipMixin,
            ContractManagementMixin,
            View
        ):
            def post(self, request, contract_id):
                contract = get_object_or_404(Contract, id=contract_id)
                success, message = self.cancel_contract(contract)
                return self.json_success(message) if success else (
                    self.json_error(message)
                )
    """

    pass
