from django.contrib.auth.models import User
from django.test import TestCase
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
