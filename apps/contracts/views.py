# apps/contracts/views.py - Views Refatoradas com Mixins e Querysets
"""
Views para gerenciamento de contratos de casamento.

Este módulo contém views para:
- Listagem e visualização de contratos
- Geração de links de assinatura
- Assinatura externa (pública, por token)
- Cancelamento e edição de contratos
- Upload de contratos externos
- Geração de PDF com QR code

Organização:
- Views de listagem e visualização
- Views de ações autenticadas (planner)
- Views públicas (assinatura externa)
- Views funcionais (PDF)
"""
import base64
import os
import traceback
from io import BytesIO

import qrcode
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import get_template
from django.views.generic import TemplateView, View
from xhtml2pdf import pisa

from apps.contracts.mixins import (ContractManagementMixin,
                                   ContractOwnershipMixin)
from apps.contracts.models import Contract
from apps.core.constants import GRADIENTS
from apps.weddings.models import Wedding


class ContractsPartialView(LoginRequiredMixin, TemplateView):
    """
    Exibe lista parcial de contratos de um casamento específico.
    
    Acesso: Apenas usuários autenticados (cerimonialistas).
    
    Contexto fornecido ao template:
        - wedding: Instância do casamento
        - contracts_list: Lista de dicionários com:
            * contract: Instância do Contract
            * gradient: Gradiente CSS para estilização
    
    URL Pattern:
        /contracts/partial/<wedding_id>/
    
    Mixins:
        - LoginRequiredMixin: Garante autenticação
    
    Nota: Verifica manualmente se o planner é dono do casamento via
          get_object_or_404 com filtro de planner.
    """
    template_name = "contracts/contracts_partial.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wedding_id = self.kwargs.get("wedding_id")
        planner = self.request.user
        wedding = get_object_or_404(
            Wedding,
            id=wedding_id,
            planner=planner
        )

        context["wedding"] = wedding

        # Usa o queryset customizado
        contracts_qs = (
            Contract.objects
            .for_wedding(wedding)
            .with_related()
        )

        context["contracts_list"] = [
            {
                "contract": contract,
                "gradient": GRADIENTS[idx % len(GRADIENTS)]
            }
            for idx, contract in enumerate(contracts_qs)
        ]
        return context


class GenerateSignatureLinkView(
    ContractOwnershipMixin,
    ContractManagementMixin,
    View
):
    """
    Gera link de assinatura digital e envia por e-mail.
    
    Acesso: Apenas cerimonialistas donos do contrato.
    
    Métodos HTTP:
        GET: Retorna JSON com informações do link de assinatura
            Response: {
                'link': str,
                'token': str,
                'expires_at': str
            }
        
        POST: Envia link de assinatura por e-mail
            Body: {'email': str}
            Response: JSON com success/error
    
    URL Pattern:
        /contracts/generate-link/<contract_id>/
    
    Mixins:
        - ContractOwnershipMixin: Garante autenticação e ownership
          (herda LoginRequiredMixin, então não precisa declarar
          explicitamente)
        - ContractManagementMixin: Fornece métodos de negócio
            * generate_signature_link()
            * send_signature_email()
            * json_success() / json_error()
    
    Raises:
        Http404: Se contrato não existir ou não pertencer ao planner
        Exception: Erros de servidor retornam JSON com mensagem
    """
    def get(self, request, contract_id):
        """
        Retorna informações do link de assinatura em formato JSON.
        
        Args:
            request: HttpRequest
            contract_id: ID do contrato
        
        Returns:
            JsonResponse com informações do link ou erro
        """
        try:
            contract = self.get_queryset().get(id=contract_id)
            link_info = self.generate_signature_link(contract)
            return JsonResponse(link_info)

        except Exception as e:
            traceback.print_exc()
            return self.json_error(f"ERRO NO SERVIDOR: {str(e)}")

    def post(self, request, contract_id):
        """
        Envia link de assinatura por e-mail para o signatário.
        
        Args:
            request: HttpRequest com 'email' no POST
            contract_id: ID do contrato
        
        Returns:
            JsonResponse com sucesso ou erro
        """
        try:
            contract = self.get_queryset().get(id=contract_id)
            email_cliente = request.POST.get('email')

            success, message = self.send_signature_email(
                contract,
                email_cliente
            )

            if success:
                return self.json_success(message)
            return self.json_error(message)

        except Exception as e:
            return self.json_error(f'Erro ao enviar e-mail: {str(e)}')


class SignContractExternalView(ContractManagementMixin, TemplateView):
    """
    Página pública para assinatura digital de contratos via token.
    
    Acesso: PÚBLICO - Não requer autenticação.
    Autenticação: Via token UUID na URL (sem login necessário).
    
    Esta view permite que fornecedores e noivos assinem contratos
    externamente sem necessidade de conta no sistema.
    
    Métodos HTTP:
        GET: Renderiza página de assinatura
            Contexto:
                - contract: Instância do contrato
                - signer_role: Role do próximo signatário
        
        POST: Processa a assinatura digital
            Body: {'signature_base64': str}
            Sucesso: Renderiza página de confirmação
            Erro: Re-renderiza página com mensagem de erro
    
    URL Pattern:
        /contracts/sign/<token>/
    
    Mixins:
        - ContractManagementMixin: Fornece métodos de assinatura
            * get_next_signer_info()
            * process_contract_signature()
    
    Security:
        - Token UUID único e não-guessable
        - Token pode ser invalidado/expirado
        - Verificação do próximo signatário esperado
        - Validação de formato e tamanho da assinatura
    
    Nota: Propositalmente NÃO herda de LoginRequiredMixin para
          permitir acesso público via token.
    """
    template_name = "contracts/external_signature.html"

    def get_context_data(self, **kwargs):
        """
        Prepara contexto para renderização da página de assinatura.
        
        Returns:
            dict: Contexto com contract e signer_role
        """
        context = super().get_context_data(**kwargs)
        token = self.kwargs.get("token")
        contract = get_object_or_404(Contract, token=token)

        next_signer_info = contract.get_next_signer_info()

        context["contract"] = contract
        context["signer_role"] = next_signer_info['role']
        return context

    def post(self, request, token):
        """
        Processa a assinatura digital enviada pelo formulário.
        
        Args:
            request: HttpRequest com signature_base64 no POST
            token: UUID token do contrato
        
        Returns:
            HttpResponse com página de sucesso ou erro
        """
        contract = get_object_or_404(Contract, token=token)
        signature_b64 = request.POST.get("signature_base64")

        success, message = self.process_contract_signature(
            contract,
            signature_b64,
            request
        )

        if success:
            return render(
                request,
                "contracts/signature_success.html",
                {"contract": contract}
            )

        return render(
            request,
            "contracts/external_signature.html",
            {"contract": contract, "error": message}
        )


def download_contract_pdf(request, contract_id):
    """
    View funcional para geração e download de PDF do contrato.
    
    Acesso: Público (sem verificação de autenticação).
    
    Funcionalidades:
        - Gera PDF a partir de template HTML
        - Inclui QR code com link para o contrato
        - Nome do arquivo inclui nome do item e parte do token
    
    Args:
        request: HttpRequest (usado para construir URL absoluta)
        contract_id: ID do contrato a ser baixado
    
    Returns:
        HttpResponse com PDF anexado ou mensagem de erro
    
    URL Pattern:
        /contracts/download-pdf/<contract_id>/
    
    Tecnologias:
        - xhtml2pdf: Conversão HTML → PDF
        - qrcode: Geração de QR code
        - PIL/Pillow: Manipulação de imagem do QR code
    
    Template usado:
        contracts/pdf_template.html
    
    TODO: Adicionar verificação de autenticação/ownership se necessário
    """
    contract = get_object_or_404(Contract, id=contract_id)
    template_path = 'contracts/pdf_template.html'

    # --- GERAÇÃO DO QR CODE ---
    link = request.build_absolute_uri(contract.get_absolute_url())

    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(link)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img_qr.save(buffer, "PNG")  # format removido, passado como posicional
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    # ---------------------------

    context = {
        'contract': contract,
        'qr_code': qr_base64
    }

    response = HttpResponse(content_type='application/pdf')
    filename = (
        f"contrato_{contract.item.name}_{str(contract.token)[:8]}.pdf"
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(
        html,
        dest=response,
        link_callback=link_callback
    )
    if pisa_status.err:
        return HttpResponse('Erro PDF <pre>' + html + '</pre>')
    return response


def link_callback(uri, rel):
    """
    Callback para resolver caminhos de recursos estáticos no PDF.
    
    Esta função é chamada pelo xhtml2pdf quando encontra referências
    a arquivos estáticos (CSS, imagens) no HTML que está sendo
    convertido para PDF.
    
    Args:
        uri: URI do recurso (pode ser relativa ou absoluta)
        rel: Caminho relativo (não usado nesta implementação)
    
    Returns:
        str: Caminho absoluto do arquivo no sistema de arquivos
             ou a URI original se não for encontrada
    
    Lógica:
        1. Se URI começa com MEDIA_URL → busca em MEDIA_ROOT
        2. Se URI começa com STATIC_URL → busca em STATIC_ROOT
        3. Caso contrário → retorna URI sem modificação
    
    Nota: Arquivos não encontrados não geram erro, apenas retorna
          a URI original (xhtml2pdf vai ignorar o recurso).
    """
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

    if not os.path.isfile(path):
        pass
    return path


class CancelContractView(
    ContractOwnershipMixin,
    ContractManagementMixin,
    View
):
    """
    Cancela um contrato e invalida seu link de assinatura.
    
    Acesso: Apenas cerimonialistas donos do contrato.
    
    Métodos HTTP:
        POST: Cancela o contrato
            Response: JSON com success/error
    
    URL Pattern:
        /contracts/cancel/<contract_id>/
    
    Mixins:
        - ContractOwnershipMixin: Garante autenticação e ownership
          através do get_queryset() filtrado
        - ContractManagementMixin: Fornece métodos de negócio
            * cancel_contract()
            * json_success() / json_error()
    
    Regras de Negócio:
        - Apenas contratos não-completos podem ser cancelados
        - Verificação via queryset.cancelable()
        - Status alterado para CANCELED
    
    Returns:
        JsonResponse: {'success': bool, 'message': str}
    
    Nota: LoginRequiredMixin é herdado via ContractOwnershipMixin,
          não precisa ser declarado explicitamente.
    """
    def post(self, request, contract_id):
        """
        Processa o cancelamento do contrato.
        
        Args:
            request: HttpRequest
            contract_id: ID do contrato a ser cancelado
        
        Returns:
            JsonResponse com resultado da operação
        """
        contract = self.get_queryset().get(id=contract_id)

        success, message = self.cancel_contract(contract)

        if success:
            return self.json_success(message)
        return self.json_error(message)


class EditContractView(
    ContractOwnershipMixin,
    ContractManagementMixin,
    View
):
    """
    Atualiza a descrição (minuta) de um contrato editável.
    
    Acesso: Apenas cerimonialistas donos do contrato.
    
    Métodos HTTP:
        POST: Atualiza descrição do contrato
            Body: {'description': str}
            Response: JSON com success/error
    
    URL Pattern:
        /contracts/edit/<contract_id>/
    
    Mixins:
        - ContractOwnershipMixin: Garante autenticação e ownership
        - ContractManagementMixin: Fornece métodos de negócio
            * update_contract_description()
            * json_success() / json_error()
    
    Regras de Negócio:
        - Apenas contratos em status DRAFT ou WAITING_PLANNER
          podem ser editados
        - Verificação via queryset.editable()
        - Descrição não pode ser vazia
    
    Returns:
        JsonResponse: {'success': bool, 'message': str}
    
    Nota: LoginRequiredMixin é herdado via ContractOwnershipMixin.
    """
    def post(self, request, contract_id):
        """
        Processa a atualização da descrição do contrato.
        
        Args:
            request: HttpRequest com 'description' no POST
            contract_id: ID do contrato a ser editado
        
        Returns:
            JsonResponse com resultado da operação
        """
        contract = self.get_queryset().get(id=contract_id)

        new_description = request.POST.get('description')
        success, message = self.update_contract_description(
            contract,
            new_description
        )

        if success:
            return self.json_success(message)
        return self.json_error(message)


class UploadContractView(
    ContractOwnershipMixin,
    ContractManagementMixin,
    View
):
    """
    Upload manual de contrato assinado externamente (físico/offline).
    
    Acesso: Apenas cerimonialistas donos do contrato.
    
    Use Case:
        Quando o contrato foi assinado de forma física (papel) ou
        através de outro sistema, o planner pode fazer upload do
        PDF final, pulando o fluxo de assinatura digital.
    
    Métodos HTTP:
        POST: Faz upload do PDF externo
            Body (multipart/form-data):
                - external_pdf: arquivo PDF
            Response: JSON com success/error
    
    URL Pattern:
        /contracts/upload/<contract_id>/
    
    Mixins:
        - ContractOwnershipMixin: Garante autenticação e ownership
        - ContractManagementMixin: Fornece métodos de negócio
            * upload_external_contract()
            * json_success() / json_error()
    
    Regras de Negócio:
        - Apenas arquivos PDF são aceitos
        - Contrato é marcado como COMPLETED
        - Hash de integridade definido como EXTERNAL_CONTRACT_HASH
        - Contrato não passa por fluxo de assinaturas digitais
    
    Returns:
        JsonResponse: {'success': bool, 'message': str}
    
    Nota: LoginRequiredMixin é herdado via ContractOwnershipMixin.
    """
    def post(self, request, contract_id):
        """
        Processa o upload do arquivo PDF externo.
        
        Args:
            request: HttpRequest com 'external_pdf' em FILES
            contract_id: ID do contrato
        
        Returns:
            JsonResponse com resultado da operação
        """
        contract = self.get_queryset().get(id=contract_id)

        pdf_file = request.FILES.get('external_pdf')
        success, message = self.upload_external_contract(
            contract,
            pdf_file
        )

        if success:
            return self.json_success(message)
        return self.json_error(message)
