from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from portfolio.models import Certification


class CertificationCreateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin", password="password123")

    def test_requires_login(self):
        url = reverse("portfolio:certification_create")
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('portfolio:login')}?next={url}")

    def test_get_shows_empty_form(self):
        self.client.login(username="admin", password="password123")
        response = self.client.get(reverse("portfolio:certification_create"))
        self.assertEqual(response.status_code, 200)

    def test_post_valid_data_creates_certification_and_redirects(self):
        self.client.login(username="admin", password="password123")

        response = self.client.post(
            reverse("portfolio:certification_create"),
            {"icon": "shield-check", "title": "基本情報技術者試験"},
        )

        self.assertRedirects(response, reverse("portfolio:dashboard"))
        self.assertEqual(Certification.objects.count(), 1)

    def test_post_invalid_data_shows_errors(self):
        self.client.login(username="admin", password="password123")

        response = self.client.post(
            reverse("portfolio:certification_create"), {"icon": "shield-check", "title": ""}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Certification.objects.count(), 0)
