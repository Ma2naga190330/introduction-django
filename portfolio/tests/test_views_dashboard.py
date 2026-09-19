from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from portfolio.models import Activity


class DashboardViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin", password="password123")

    def test_requires_login(self):
        response = self.client.get(reverse("portfolio:dashboard"))
        self.assertRedirects(
            response, f"{reverse('portfolio:login')}?next={reverse('portfolio:dashboard')}"
        )

    def test_shows_registered_data_when_logged_in(self):
        Activity.objects.create(icon="trophy", title="北九州Techハッカソン2025")
        self.client.login(username="admin", password="password123")

        response = self.client.get(reverse("portfolio:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "北九州Techハッカソン2025")
