# from datetime import date  # Usado no teste comentado

from django.test import TestCase
from django.urls import reverse
from parameterized import parameterized


class TestPagesViews(TestCase):
    """Testa as views estáticas da app 'pages'."""

    @parameterized.expand(
        [
            # Cada tupla representa um caso de teste (nome, url, template, conteúdo esperado)
            ("home_page", "pages:home", "pages/home.html", "Gestão de Casamentos"),
            ("contact_us_page", "pages:contact_us", "pages/contact-us.html", "Fale Conosco"),
        ]
    )
    def test_static_pages_render_correctly(self, _, url_name, template_name, expected_content):
        """Verifica se as páginas estáticas renderizam corretamente com o template e conteúdo esperado."""
        url = reverse(url_name)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name)
        self.assertContains(response, expected_content)

    # Exemplo de teste adicional (comentado)
    # def test_home_view_provides_correct_context(self):
    #     """Verifica se a HomeView adiciona o ano atual ao contexto."""
    #     url = reverse("pages:home")
    #     response = self.client.get(url)
    #     expected_year = date.today().year
    #     self.assertIn("current_year", response.context)
    #     self.assertEqual(response.context["current_year"], expected_year)
    #     self.assertContains(response, str(expected_year))
