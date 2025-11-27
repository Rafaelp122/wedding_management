import logging

from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.generic import TemplateView, View

from apps.core.mixins.auth import RedirectAuthenticatedUserMixin

from .forms import ContactForm

# Configura o logger para registrar erros de envio de e-mail
logger = logging.getLogger(__name__)


class HomeView(RedirectAuthenticatedUserMixin, TemplateView):
    """
    Renderiza a página inicial (Landing Page) pública do site.

    Comportamento:
    - Usuários autenticados são redirecionados automaticamente para
      a área logada ('my_weddings') através do RedirectAuthenticatedUserMixin.
    - Usuários anônimos veem a Landing Page com o formulário de contato.
    """

    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        """
        Adiciona o formulário de contato e os ícones de UI ao contexto.
        """
        context = super().get_context_data(**kwargs)
        context["contact_form"] = ContactForm()

        # Define os ícones usados nos inputs do formulário
        context["form_icons"] = {
            "name": "fas fa-user",
            "email": "fas fa-envelope",
            "message": "fas fa-align-left",
        }
        return context


class ContactFormSubmitView(View):
    """
    Endpoint exclusivo para processamento do formulário de contato via HTMX.

    Métodos suportados:
    - POST: Recebe os dados, valida, salva no banco e envia e-mail.
    """

    def post(self, request, *args, **kwargs):
        """
        Processa a submissão do formulário.

        Fluxo de Sucesso (HTTP 200):
        1. Salva a mensagem no banco de dados (ContactInquiry).
        2. Envia notificação por e-mail para o administrador.
        3. Retorna o template parcial de sucesso ('_contact_success.html').

        Fluxo de Erro (HTTP 400):
        1. Retorna o template do formulário ('_contact_form_partial.html')
           contendo os erros de validação para feedback visual.
        """
        form = ContactForm(request.POST)

        if form.is_valid():
            # Salva no banco de dados
            inquiry = form.save()

            # Prepara o e-mail
            subject = f"Nova Mensagem de Contato de {inquiry.name}"
            context_email = {
                "name": inquiry.name,
                "email": inquiry.email,
                "message": inquiry.message,
                "created_at": inquiry.created_at,
            }
            body = render_to_string(
                "pages/emails/contact_notification.txt", context_email
            )

            # Tenta enviar o e-mail (com tratamento de erro silencioso para o usuário)
            try:
                send_mail(
                    subject=subject,
                    message=body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.ADMIN_EMAIL],
                    fail_silently=False,
                )
            except Exception as e:
                # Loga o erro para o admin investigar, mas não quebra a experiência do usuário
                logger.error(f"Erro ao enviar e-mail de contato: {e}", exc_info=True)
                pass

            # Retorna a resposta HTMX de sucesso
            return render(request, "pages/partials/home/_contact_success.html")

        # --- FLUXO DE ERRO ---

        # Recriamos o dicionário de ícones, pois ele não persiste no POST
        # e é necessário para renderizar o formulário com erros corretamente.
        form_icons = {
            "name": "fas fa-user",
            "email": "fas fa-envelope",
            "message": "fas fa-align-left",
        }

        # Retorna o formulário com os erros de validação
        response = render(
            request,
            "pages/partials/home/_contact_form_partial.html",
            {"contact_form": form, "form_icons": form_icons},
        )

        # Define Status 400 (Bad Request) para indicar erro ao HTMX
        response.status_code = 400
        return response
