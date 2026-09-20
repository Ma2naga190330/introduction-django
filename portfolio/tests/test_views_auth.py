from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse


class LoginViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin", password="password123")

    def test_get_shows_login_form(self):
        response = self.client.get(reverse("portfolio:login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ユーザー名")

    def test_post_with_correct_credentials_redirects_to_dashboard(self):
        response = self.client.post(
            reverse("portfolio:login"),
            {"username": "admin", "password": "password123"},
        )
        self.assertRedirects(response, reverse("portfolio:dashboard"))

    def test_post_with_wrong_credentials_shows_error(self):
        response = self.client.post(
            reverse("portfolio:login"),
            {"username": "admin", "password": "wrong-password"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ユーザー名またはパスワードが正しくありません。")

    def test_post_without_csrf_token_is_forbidden(self):
        client = Client(enforce_csrf_checks=True)

        response = client.post(
            reverse("portfolio:login"), {"username": "admin", "password": "password123"}
        )

        self.assertEqual(response.status_code, 403)
        self.assertNotIn("_auth_user_id", client.session)

    def test_form_has_autofill_hints(self):
        response = self.client.get(reverse("portfolio:login"))
        self.assertContains(response, 'autocomplete="username"')
        self.assertContains(response, 'autocomplete="current-password"')
        self.assertContains(response, "autofocus")


class LogoutViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin", password="password123")

    def test_post_while_logged_in_redirects_to_profile(self):
        self.client.login(username="admin", password="password123")
        response = self.client.post(reverse("portfolio:logout"))
        self.assertRedirects(response, reverse("portfolio:profile"))

    def test_get_is_not_allowed(self):
        self.client.login(username="admin", password="password123")
        response = self.client.get(reverse("portfolio:logout"))
        self.assertEqual(response.status_code, 405)

    def test_requires_login(self):
        response = self.client.post(reverse("portfolio:logout"))
        self.assertRedirects(
            response, f"{reverse('portfolio:login')}?next={reverse('portfolio:logout')}"
        )

    def test_post_clears_the_session(self):
        self.client.login(username="admin", password="password123")
        self.assertIn("_auth_user_id", self.client.session)

        self.client.post(reverse("portfolio:logout"))

        self.assertNotIn("_auth_user_id", self.client.session)

    def test_post_without_csrf_token_is_forbidden(self):
        client = Client(enforce_csrf_checks=True)
        client.login(username="admin", password="password123")

        response = client.post(reverse("portfolio:logout"))

        self.assertEqual(response.status_code, 403)
        self.assertIn("_auth_user_id", client.session)
