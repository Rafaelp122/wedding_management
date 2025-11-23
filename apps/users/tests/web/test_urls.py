from django.test import SimpleTestCase
from django.urls import resolve, reverse

from apps.users.web import allauth_views, views


class UsersUrlsTest(SimpleTestCase):
    """
    Testa as URLs do app users.
    As URLs de signup, signin e logout agora são gerenciadas por views
    customizadas que herdam do django-allauth.
    """

    def test_signup_url_resolves(self):
        """Testa que a URL de signup resolve para view customizada."""
        url = reverse("account_signup")
        resolved = resolve(url)
        self.assertEqual(
            resolved.func.view_class, allauth_views.CustomSignupView
        )

    def test_signin_url_resolves(self):
        """Testa que a URL de login resolve para view customizada."""
        url = reverse("account_login")
        resolved = resolve(url)
        self.assertEqual(
            resolved.func.view_class, allauth_views.CustomLoginView
        )

    def test_logout_url_resolves(self):
        """Testa que a URL de logout resolve para view customizada."""
        url = reverse("account_logout")
        resolved = resolve(url)
        self.assertEqual(
            resolved.func.view_class, allauth_views.CustomLogoutView
        )

    def test_edit_profile_url_resolves(self):
        """Testa a URL customizada de edição de perfil."""
        url = reverse("users:edit_profile")
        self.assertEqual(resolve(url).func.view_class, views.EditProfileView)
