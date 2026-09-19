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


class CertificationUpdateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin", password="password123")
        self.certification = Certification.objects.create(icon="shield-check", title="既存の資格")

    def test_requires_login(self):
        url = reverse("portfolio:certification_update", args=[self.certification.pk])
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('portfolio:login')}?next={url}")

    def test_get_prefills_existing_data(self):
        self.client.login(username="admin", password="password123")
        response = self.client.get(
            reverse("portfolio:certification_update", args=[self.certification.pk])
        )
        self.assertContains(response, "既存の資格")

    def test_post_valid_data_updates_certification(self):
        self.client.login(username="admin", password="password123")

        response = self.client.post(
            reverse("portfolio:certification_update", args=[self.certification.pk]),
            {"icon": "shield-check", "title": "更新後の資格"},
        )

        self.assertRedirects(response, reverse("portfolio:dashboard"))
        self.certification.refresh_from_db()
        self.assertEqual(self.certification.title, "更新後の資格")

    def test_get_with_unknown_pk_returns_404(self):
        self.client.login(username="admin", password="password123")
        response = self.client.get(reverse("portfolio:certification_update", args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_post_invalid_data_shows_errors(self):
        self.client.login(username="admin", password="password123")

        response = self.client.post(
            reverse("portfolio:certification_update", args=[self.certification.pk]),
            {"icon": "shield-check", "title": ""},
        )

        self.assertEqual(response.status_code, 200)
        self.certification.refresh_from_db()
        self.assertEqual(self.certification.title, "既存の資格")


class CertificationDeleteViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin", password="password123")
        self.certification = Certification.objects.create(icon="shield-check", title="削除対象の資格")

    def test_requires_login(self):
        url = reverse("portfolio:certification_delete", args=[self.certification.pk])
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('portfolio:login')}?next={url}")

    def test_get_shows_confirmation(self):
        self.client.login(username="admin", password="password123")
        response = self.client.get(
            reverse("portfolio:certification_delete", args=[self.certification.pk])
        )
        self.assertContains(response, "削除対象の資格")

    def test_post_confirm_yes_deletes_certification(self):
        self.client.login(username="admin", password="password123")

        response = self.client.post(
            reverse("portfolio:certification_delete", args=[self.certification.pk]),
            {"confirm": "yes"},
        )

        self.assertRedirects(response, reverse("portfolio:dashboard"))
        self.assertEqual(Certification.objects.count(), 0)

    def test_get_with_unknown_pk_returns_404(self):
        self.client.login(username="admin", password="password123")
        response = self.client.get(reverse("portfolio:certification_delete", args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_post_confirm_no_keeps_certification(self):
        self.client.login(username="admin", password="password123")

        response = self.client.post(
            reverse("portfolio:certification_delete", args=[self.certification.pk]),
            {"confirm": "no"},
        )

        self.assertRedirects(response, reverse("portfolio:dashboard"))
        self.assertEqual(Certification.objects.count(), 1)
