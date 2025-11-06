# import datetime

from django.test import TestCase
from django.urls import reverse
from parameterized import parameterized


class TestPagesViews(TestCase):
    """Testa as Class-Based Views da app 'pages'."""

    @parameterized.expand(
        [
            # Tupla de argumentos: (nome_do_caso, url_name, template_name, expected_content)
            ("home_page", "pages:home", "pages/home.html", "Gestão de Casamentos"),
            (
                "contact_us_page",
                "pages:contact_us",
                "pages/contact-us.html",
                "Fale Conosco",
            ),
        ]
    )
    def test_static_pages_render_correctly(
        self, _, url_name, template_name, expected_content
    ):
        """
        Verifica se as páginas estáticas renderizam corretamente.
        Este teste é parametrizado e cada caso será executado individualmente.
        """
        url = reverse(url_name)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name)
        self.assertContains(response, expected_content)

    # def test_home_view_provides_correct_context(self):
    #     """
    #     Verifica se a HomeView adiciona o 'current_year' ao contexto corretamente.
    #     """
    #     url = reverse("pages:home")
    #     response = self.client.get(url)

    #     # O ano atual, baseado na data do sistema onde o teste roda
    #     expected_year = datetime.date.today().year

    #     # Verifica se o ano está no contexto da resposta
    #     self.assertIn('current_year', response.context)
    #     self.assertEqual(response.context['current_year'], expected_year)

    #     # Um teste ainda melhor é verificar se o ano foi renderizado no HTML
    #     self.assertContains(response, str(expected_year))
