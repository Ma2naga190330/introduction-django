from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from portfolio.models import Skill


class SkillCreateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin", password="password123")

    def test_requires_login(self):
        url = reverse("portfolio:skill_create")
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('portfolio:login')}?next={url}")

    def test_get_shows_empty_form(self):
        self.client.login(username="admin", password="password123")
        response = self.client.get(reverse("portfolio:skill_create"))
        self.assertEqual(response.status_code, 200)

    def test_post_valid_data_creates_skill_and_redirects(self):
        self.client.login(username="admin", password="password123")

        response = self.client.post(
            reverse("portfolio:skill_create"), {"name": "Python / Django"}
        )

        self.assertRedirects(response, reverse("portfolio:dashboard"))
        self.assertEqual(Skill.objects.count(), 1)

    def test_post_invalid_data_shows_errors(self):
        self.client.login(username="admin", password="password123")

        response = self.client.post(reverse("portfolio:skill_create"), {"name": ""})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Skill.objects.count(), 0)

    def test_post_duplicate_name_shows_errors(self):
        Skill.objects.create(name="Python / Django")
        self.client.login(username="admin", password="password123")

        response = self.client.post(
            reverse("portfolio:skill_create"), {"name": "Python / Django"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Skill.objects.count(), 1)


class SkillUpdateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin", password="password123")
        self.skill = Skill.objects.create(name="既存のスキル")

    def test_requires_login(self):
        url = reverse("portfolio:skill_update", args=[self.skill.pk])
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('portfolio:login')}?next={url}")

    def test_get_prefills_existing_data(self):
        self.client.login(username="admin", password="password123")
        response = self.client.get(reverse("portfolio:skill_update", args=[self.skill.pk]))
        self.assertContains(response, "既存のスキル")

    def test_post_valid_data_updates_skill(self):
        self.client.login(username="admin", password="password123")

        response = self.client.post(
            reverse("portfolio:skill_update", args=[self.skill.pk]),
            {"name": "更新後のスキル"},
        )

        self.assertRedirects(response, reverse("portfolio:dashboard"))
        self.skill.refresh_from_db()
        self.assertEqual(self.skill.name, "更新後のスキル")

    def test_get_with_unknown_pk_returns_404(self):
        self.client.login(username="admin", password="password123")
        response = self.client.get(reverse("portfolio:skill_update", args=[9999]))
        self.assertEqual(response.status_code, 404)
