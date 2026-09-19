from django.test import TestCase
from django.urls import reverse

from portfolio.models import Activity, Certification, Skill


class ProfileViewTest(TestCase):
    def test_get_returns_200(self):
        response = self.client.get(reverse("portfolio:profile"))
        self.assertEqual(response.status_code, 200)

    def test_shows_registered_data(self):
        Activity.objects.create(icon="trophy", title="北九州Techハッカソン2025")
        Certification.objects.create(icon="shield-check", title="基本情報技術者試験")
        Skill.objects.create(name="Python / Django")

        response = self.client.get(reverse("portfolio:profile"))

        self.assertContains(response, "北九州Techハッカソン2025")
        self.assertContains(response, "基本情報技術者試験")
        self.assertContains(response, "Python / Django")

    def test_shows_empty_state_when_no_data(self):
        response = self.client.get(reverse("portfolio:profile"))
        self.assertContains(response, "登録された活動実績はまだありません。")
