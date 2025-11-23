"""
Mixins para views de contratos.
Contém lógicas reutilizáveis para autorização, geração de PDF e tracking.
"""
import logging
from typing import Optional

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from xhtml2pdf import pisa

from apps.contracts.models import Contract

logger = logging.getLogger(__name__)


class ClientIPMixin:
    """
    Mixin genérico para extrair o IP do cliente de requisições.

    Útil para funcionalidades de auditoria, logging e tracking.
    Trata corretamente headers de proxy (X-Forwarded-For).

    Usage:
        class MyView(ClientIPMixin, View):
            def get(self, request):
                ip = self.get_client_ip()
                # usar o IP para auditoria
    """

    request: HttpRequest

    def get_client_ip(self) -> str:
        """
        Extrai o endereço IP do cliente para fins de auditoria.

        Trata corretamente requisições através de proxies,
        extraindo o IP original do header X-Forwarded-For.

        Returns:
            str: Endereço IP do cliente ou 'unknown' se não disponível
        """
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Pega o primeiro IP da cadeia (cliente original)
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = self.request.META.get('REMOTE_ADDR', 'unknown')
        return ip


class ContractOwnershipMixin(LoginRequiredMixin):
    """
    Mixin para verificar se o usuário tem permissão de acessar um contrato.

    Valida que o usuário logado é o planner responsável pelo casamento
    vinculado ao contrato.

    Attributes:
        contract: Instância do Contract (deve ser definida pela view)

    Usage:
        class MyContractView(ContractOwnershipMixin, View):
            def get(self, request, contract_id):
                contract = self.get_contract_or_403(contract_id)
                # usuário tem permissão garantida
    """

    request: HttpRequest

    def get_contract_or_403(self, contract_id: int) -> Contract:
        """
        Obtém o contrato e valida permissões do usuário.

        Args:
            contract_id: ID do contrato

        Returns:
            Contract: Instância do contrato se usuário tiver permissão

        Raises:
            PermissionDenied: Se o usuário não for o planner do casamento
        """
        contract = get_object_or_404(Contract, id=contract_id)

        # Verifica se o usuário tem permissão
        if contract.wedding.planner != self.request.user:
            logger.warning(
                f"Acesso negado ao contrato {contract_id} "
                f"por {self.request.user.username}"
            )
            raise PermissionDenied(
                "Você não tem permissão para acessar este contrato."
            )

        return contract


class TokenAccessMixin:
    """
    Mixin para acessar contratos via token UUID (acesso público).

    Usado em views que permitem acesso externo via link único,
    como assinatura de contratos por fornecedores/clientes.

    Usage:
        class SignContractView(TokenAccessMixin, TemplateView):
            def get_context_data(self, **kwargs):
                context = super().get_context_data(**kwargs)
                contract = self.get_contract_by_token()
                context['contract'] = contract
                return context
    """

    kwargs: dict

    def get_contract_by_token(self) -> Contract:
        """
        Obtém o contrato usando o token UUID da URL.

        Returns:
            Contract: Instância do contrato

        Raises:
            Http404: Se o token não for válido
        """
        token = self.kwargs.get("token")
        contract = get_object_or_404(Contract, token=token)
        return contract


class PDFResponseMixin:
    """
    Mixin para gerar respostas em PDF usando xhtml2pdf.

    Renderiza templates Django como PDFs com suporte a arquivos
    estáticos e media (CSS, imagens).

    Attributes:
        pdf_template_name: Nome do template a ser renderizado como PDF
        pdf_filename: Nome do arquivo PDF (pode incluir variáveis)

    Usage:
        class DownloadPDFView(PDFResponseMixin, View):
            pdf_template_name = 'documents/contract.html'

            def get(self, request, contract_id):
                contract = Contract.objects.get(id=contract_id)
                return self.render_to_pdf(
                    context={'contract': contract},
                    filename=f'contrato_{contract.id}.pdf'
                )
    """

    request: HttpRequest
    pdf_template_name: Optional[str] = None

    def render_to_pdf(
        self,
        context: dict,
        filename: str,
        template_name: Optional[str] = None
    ) -> HttpResponse:
        """
        Renderiza um template como PDF e retorna como download.

        Args:
            context: Dicionário de contexto para o template
            filename: Nome do arquivo PDF para download
            template_name: Template a usar (sobrescreve pdf_template_name)

        Returns:
            HttpResponse: Resposta HTTP com PDF ou mensagem de erro
        """
        template_path = template_name or self.pdf_template_name

        if not template_path:
            logger.error("pdf_template_name não definido")
            return HttpResponse(
                'Configuração de template incorreta.',
                status=500
            )

        # Prepara a resposta HTTP
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        # Renderiza o template
        template = get_template(template_path)
        html = template.render(context)

        # Gera o PDF
        pisa_status = pisa.CreatePDF(
            html,
            dest=response,
            link_callback=self._pdf_link_callback
        )

        if pisa_status.err:
            logger.error(
                f"Erro ao gerar PDF: {template_path}",
                exc_info=True
            )
            return HttpResponse(
                'Erro ao gerar PDF. Por favor, tente novamente.',
                status=500
            )

        return response

    @staticmethod
    def _pdf_link_callback(uri: str, rel: str) -> str:
        """
        Callback para resolver URLs de arquivos estáticos e media no PDF.

        Converte URLs relativas para caminhos absolutos no sistema de
        arquivos, permitindo que o xhtml2pdf acesse CSS, imagens, etc.

        Args:
            uri: URI do recurso (pode ser relativa ou absoluta)
            rel: Caminho relativo (não usado)

        Returns:
            str: Caminho absoluto do arquivo ou URI original se não encontrado
        """
        import os

        sUrl = settings.STATIC_URL
        sRoot = settings.STATIC_ROOT
        mUrl = settings.MEDIA_URL
        mRoot = settings.MEDIA_ROOT

        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri

        # Retorna o path se existir, caso contrário retorna a URI original
        if os.path.isfile(path):
            return path
        return uri
