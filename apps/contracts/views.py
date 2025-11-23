# terraria - Versão Final Pós-Conflito (Com QR Code, Email e Auditoria)
import base64
import hashlib
import os
import traceback
import qrcode
from io import BytesIO
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.base import ContentFile
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import get_template
from django.utils import timezone
from django.views.generic import TemplateView, View
from xhtml2pdf import pisa
from django.core.mail import send_mail

from apps.contracts.models import Contract
from apps.core.constants import GRADIENTS
from apps.weddings.models import Wedding


def get_client_ip(request):
    """Função auxiliar para pegar o IP do usuário para auditoria."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class ContractsPartialView(LoginRequiredMixin, TemplateView):
    template_name = "contracts/contracts_partial.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wedding_id = self.kwargs.get("wedding_id")
        planner = self.request.user
        wedding = get_object_or_404(Wedding, id=wedding_id, planner=planner)
        
        context["wedding"] = wedding
        contracts_qs = Contract.objects.filter(item__wedding=wedding).select_related("item")

        context["contracts_list"] = [
            {"contract": contract, "gradient": GRADIENTS[idx % len(GRADIENTS)]}
            for idx, contract in enumerate(contracts_qs)
        ]
        return context


class GenerateSignatureLinkView(LoginRequiredMixin, View):
    def get(self, request, contract_id):
        try:
            contract = get_object_or_404(Contract, id=contract_id)
            
            try:
                link = request.build_absolute_uri(contract.get_absolute_url())
            except Exception as e:
                return JsonResponse({"link": f"ERRO NA URL: {str(e)}"})
            
            next_signer = "Alguém"
            
            if contract.status == "WAITING_PLANNER":
                next_signer = "Você (Cerimonialista)"
                
            elif contract.status == "WAITING_SUPPLIER":
                if contract.supplier:
                    nome_fornecedor = getattr(contract.supplier, 'name', str(contract.supplier))
                    next_signer = f"Fornecedor ({nome_fornecedor})"
                else:
                    next_signer = "Fornecedor (Não vinculado)"
                    
            elif contract.status == "WAITING_COUPLE":
                if contract.wedding:
                     nome_casal = getattr(contract.wedding, 'couple_name', str(contract.wedding))
                     next_signer = f"Noivos ({nome_casal})"
                else:
                    next_signer = "Noivos"
                
            return JsonResponse({
                "link": link,
                "status": contract.status,
                "message": f"Próximo a assinar: {next_signer}"
            })

        except Exception as e:
            traceback.print_exc()
            return JsonResponse({"link": f"ERRO NO SERVIDOR: {str(e)}"})
    
    def post(self, request, contract_id):
        try:
            contract = get_object_or_404(Contract, id=contract_id)
            email_cliente = request.POST.get('email')
            link = request.build_absolute_uri(contract.get_absolute_url())
            
            assunto = f"Assinatura Pendente: {contract.item.name}"
            mensagem = f"""
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
                assunto,
                mensagem,
                settings.DEFAULT_FROM_EMAIL,
                [email_cliente],
                fail_silently=False,
            )
            
            return JsonResponse({'success': True, 'message': f'E-mail enviado com sucesso para {email_cliente}!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erro ao enviar e-mail: {str(e)}'})


class SignContractExternalView(TemplateView):
    template_name = "contracts/external_signature.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        token = self.kwargs.get("token")
        contract = get_object_or_404(Contract, token=token)
        
        signer_role = None
        if contract.status == "WAITING_PLANNER":
            signer_role = "Cerimonialista"
        elif contract.status == "WAITING_SUPPLIER":
            signer_role = "Fornecedor"
        elif contract.status == "WAITING_COUPLE":
            signer_role = "Noivos (Contratantes)"
            
        context["contract"] = contract
        context["signer_role"] = signer_role
        return context

    def post(self, request, token):
        contract = get_object_or_404(Contract, token=token)
        signature_b64 = request.POST.get("signature_base64")
        client_ip = get_client_ip(request)

        if not signature_b64:
            return render(request, self.template_name, {"contract": contract, "error": "Assinatura vazia."})

        try:
            if ';base64,' in signature_b64:
                format, imgstr = signature_b64.split(';base64,') 
                ext = format.split('/')[-1] 
                data = ContentFile(base64.b64decode(imgstr), name=f'sig_{contract.status}_{contract.token}.{ext}')

                if contract.status == "WAITING_PLANNER":
                    contract.planner_signature = data
                    contract.planner_signed_at = timezone.now()
                    contract.planner_ip = client_ip
                    contract.status = "WAITING_SUPPLIER" 
                    
                elif contract.status == "WAITING_SUPPLIER":
                    contract.supplier_signature = data
                    contract.supplier_signed_at = timezone.now()
                    contract.supplier_ip = client_ip
                    contract.status = "WAITING_COUPLE" 
                    
                elif contract.status == "WAITING_COUPLE":
                    contract.couple_signature = data
                    contract.couple_signed_at = timezone.now()
                    contract.couple_ip = client_ip
                    contract.status = "COMPLETED" 
                    
                    hash_input = f"{contract.id}-{str(contract.planner_signed_at)}-{str(contract.supplier_signed_at)}-{timezone.now()}"
                    contract.integrity_hash = hashlib.sha256(hash_input.encode()).hexdigest()

                contract.save()
                return render(request, "contracts/signature_success.html", {"contract": contract})
                
        except Exception as e:
            print(f"Erro ao processar assinatura: {e}")
            traceback.print_exc()
            return render(request, self.template_name, {"contract": contract, "error": f"Erro técnico: {str(e)}"})

        return render(request, self.template_name, {"contract": contract})


def download_contract_pdf(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    template_path = 'contracts/pdf_template.html'
    
    # --- GERAÇÃO DO QR CODE ---
    link = request.build_absolute_uri(contract.get_absolute_url())
    
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(link)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img_qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    # ---------------------------

    context = {
        'contract': contract,
        'qr_code': qr_base64
    }
    
    response = HttpResponse(content_type='application/pdf')
    filename = f"contrato_{contract.item.name}_{str(contract.token)[:8]}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response, link_callback=link_callback)
    if pisa_status.err:
       return HttpResponse('Erro PDF <pre>' + html + '</pre>')
    return response


def link_callback(uri, rel):
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