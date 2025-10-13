from django.views.generic import TemplateView


class HomeView(TemplateView):
    """Renderiza a página inicial."""
    template_name = "pages/home.html"


class ContactUsView(TemplateView):
    """Renderiza a página de contato."""
    template_name = "pages/contact-us.html"
