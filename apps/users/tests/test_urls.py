from django.contrib.auth import views as auth_views
from django.test import SimpleTestCase
from django.urls import resolve, reverse

from apps.users import views


class UsersUrlsTest(SimpleTestCase):
    def test_signup_url_resolves(self):
        url = reverse("users:sign_up")
        self.assertEqual(resolve(url).func.view_class, views.SignUpView)

    def test_signin_url_resolves(self):
        url = reverse("users:sign_in")
        self.assertEqual(resolve(url).func.view_class, views.SignInView)

    def test_logout_url_resolves(self):
        url = reverse("users:logout")
        self.assertEqual(resolve(url).func.view_class, auth_views.LogoutView)

    def test_edit_profile_url_resolves(self):
        url = reverse("users:edit_profile")
        self.assertEqual(resolve(url).func.view_class, views.EditProfileView)
