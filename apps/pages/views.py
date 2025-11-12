from django.views.generic import TemplateView

from apps.core.utils.view_mixins import RedirectAuthenticatedUserMixin


# Página inicial do site
class HomeView(RedirectAuthenticatedUserMixin, TemplateView):
    template_name = "pages/home.html"
