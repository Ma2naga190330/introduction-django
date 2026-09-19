from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from portfolio.models import Activity


class ActivityCreateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin", password="password123")

    def test_requires_login(self):
        url = reverse("portfolio:activity_create")
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('portfolio:login')}?next={url}")

    def test_get_shows_empty_form(self):
        self.client.login(username="admin", password="password123")
        response = self.client.get(reverse("portfolio:activity_create"))
        self.assertEqual(response.status_code, 200)

    def test_post_valid_data_creates_activity_and_redirects(self):
        self.client.login(username="admin", password="password123")

        response = self.client.post(
            reverse("portfolio:activity_create"),
            {"icon": "trophy", "title": "北九州Techハッカソン2025", "tags": "Winner"},
        )

        self.assertRedirects(response, reverse("portfolio:dashboard"))
        self.assertEqual(Activity.objects.count(), 1)
        self.assertEqual(Activity.objects.first().tags.first().name, "Winner")

    def test_post_invalid_data_shows_errors(self):
        self.client.login(username="admin", password="password123")

        response = self.client.post(
            reverse("portfolio:activity_create"), {"icon": "trophy", "title": "", "tags": ""}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Activity.objects.count(), 0)
