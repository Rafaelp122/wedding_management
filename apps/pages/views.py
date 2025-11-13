from apps.core.utils.view_mixins import RedirectAuthenticatedUserMixin
from django.shortcuts import render
from django.views.generic import View, TemplateView
from .forms import ContactForm
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


class HomeView(RedirectAuthenticatedUserMixin, TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contact_form'] = ContactForm
        context['form_icons'] = {
            'name': 'fas fa-user',
            'email': 'fas fa-envelope',
            'message': 'fas fa-align-left',
        }
        return context


class ContactFormSubmitView(View):
    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)

        if form.is_valid():
            # Salva no banco de dados
            inquiry = form.save()

            # Prepara o e-mail
            subject = f"Nova Mensagem de Contato de {inquiry.name}"
            context_email = {
                'name': inquiry.name,
                'email': inquiry.email,
                'message': inquiry.message,
                'created_at': inquiry.created_at,
            }
            body = render_to_string(
                "pages/emails/contact_notification.txt",
                context_email
            )

            try:
                send_mail(
                    subject=subject,
                    message=body,  # Corpo do e-mail (texto simples)
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.ADMIN_EMAIL],
                    fail_silently=False,
                )
            except Exception as e:
                # Opcional: faz log do erro de e-mail, mas não quebra
                print(f"Erro ao enviar e-mail de contato: {e}")
                pass

            # Retorna a resposta HTMX de sucesso
            return render(request, "pages/partials/home/_contact_success.html")

        # Se o formulário for inválido, retorna o formulário com erros
        # O HTMX vai substituir o formulário, agora mostrando os erros
        response = render(
            request,
            "pages/partials/_contact_form_partial.html",
            {'contact_form': form}
        )
        # Define o status como 400 para que o HTMX saiba que foi um erro
        response.status_code = 400
        return response
