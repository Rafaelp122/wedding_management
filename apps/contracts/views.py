"""
Views para gerenciamento de contratos tripartites.
Inclui funcionalidades de geração de links de assinatura,
assinatura digital e download de contratos em PDF.
"""
import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.generic import TemplateView, View

from apps.contracts.mixins import (ClientIPMixin, ContractOwnershipMixin,
                                   PDFResponseMixin, TokenAccessMixin)
from apps.contracts.models import Contract
from apps.core.constants import GRADIENTS
from apps.weddings.models import Wedding

logger = logging.getLogger(__name__)


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
    """Gera link de assinatura para contratos."""

    def get(self, request, contract_id):
        try:
            contract = get_object_or_404(Contract, id=contract_id)

            try:
                link = request.build_absolute_uri(
                    contract.get_absolute_url()
                )
            except Exception as e:
                logger.error(
                    f"Erro ao gerar URL para contrato {contract_id}: {e}"
                )
                return JsonResponse({"link": f"ERRO NA URL: {str(e)}"})

            # Usa o método do model para obter informações do próximo assinante
            next_signer_info = contract.get_next_signer_info()

            return JsonResponse({
                "link": link,
                "status": contract.status,
                "message": f"Próximo a assinar: {next_signer_info['name']}"
            })

        except Exception as e:
            logger.error(
                f"Erro ao gerar link de assinatura: {e}",
                exc_info=True
            )
            return JsonResponse({
                "link": f"ERRO NO SERVIDOR: {str(e)}"
            })


class SignContractExternalView(TokenAccessMixin, ClientIPMixin, TemplateView):
    template_name = "contracts/external_signature.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contract = self.get_contract_by_token()

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
        """Processa a assinatura digital do contrato."""
        contract = self.get_contract_by_token()
        signature_b64 = request.POST.get("signature_base64")
        client_ip = self.get_client_ip()

        if not signature_b64:
            return render(
                request,
                self.template_name,
                {
                    "contract": contract,
                    "error": "Por favor, desenhe sua assinatura."
                }
            )

        try:
            # Usa o método do model para processar a assinatura
            contract.process_signature(signature_b64, client_ip)
            return render(
                request,
                "contracts/signature_success.html",
                {"contract": contract}
            )

        except ValueError as e:
            # Erro de validação (assinatura inválida)
            logger.warning(
                f"Assinatura inválida para contrato {contract.id}: {e}"
            )
            return render(
                request,
                self.template_name,
                {
                    "contract": contract,
                    "error": "Formato de assinatura inválido."
                }
            )

        except RuntimeError as e:
            # Erro de status (contrato em estado inválido)
            logger.error(
                f"Erro de status ao assinar contrato {contract.id}: {e}"
            )
            return render(
                request,
                self.template_name,
                {
                    "contract": contract,
                    "error": "Este contrato não pode mais ser assinado."
                }
            )

        except Exception as e:
            # Erro inesperado
            logger.error(
                f"Erro ao processar assinatura do contrato {contract.id}: {e}",
                exc_info=True
            )
            return render(
                request,
                self.template_name,
                {
                    "contract": contract,
                    "error": "Erro ao processar assinatura. Tente novamente."
                }
            )


class DownloadContractPDFView(ContractOwnershipMixin, PDFResponseMixin, View):
    """
    View protegida para download de contratos em PDF.
    Apenas usuários autenticados vinculados ao casamento podem baixar.
    """

    pdf_template_name = 'contracts/pdf_template.html'

    def get(self, request, contract_id):
        # Usa o mixin para validar permissões
        contract = self.get_contract_or_403(contract_id)

        # Prepara o contexto com informações adicionais
        context = {
            'contract': contract,
            'signatures_status': contract.get_signatures_status(),
            'is_fully_signed': contract.is_fully_signed(),
            'generated_at': timezone.now()
        }

        # Prepara o filename com informações relevantes
        status_suffix = "COMPLETO" if contract.is_fully_signed() else "PARCIAL"
        filename = (
            f"contrato_{contract.item.name}_{status_suffix}_"
            f"{str(contract.token)[:8]}.pdf"
        )

        # Usa o mixin para gerar o PDF
        return self.render_to_pdf(
            context=context,
            filename=filename
        )
