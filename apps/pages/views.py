from django.views.generic import TemplateView


# Página inicial do site
class HomeView(TemplateView):
    template_name = "pages/home.html"


# Página de contato
class ContactUsView(TemplateView):
    template_name = "pages/contact-us.html"
