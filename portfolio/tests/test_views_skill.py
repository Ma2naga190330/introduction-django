from django.contrib.auth.models import User
from django.test import Client, TestCase
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

    def test_unauthenticated_post_is_rejected_and_creates_nothing(self):
        url = reverse("portfolio:skill_create")

        response = self.client.post(url, {"name": "不正な登録"})

        self.assertRedirects(response, f"{reverse('portfolio:login')}?next={url}")
        self.assertEqual(Skill.objects.count(), 0)

    def test_success_message_is_shown_on_dashboard(self):
        self.client.login(username="admin", password="password123")

        response = self.client.post(
            reverse("portfolio:skill_create"), {"name": "新しいスキル"}, follow=True
        )

        self.assertContains(response, "スキルを登録しました。")

    def test_invalid_post_shows_no_success_message(self):
        self.client.login(username="admin", password="password123")

        response = self.client.post(reverse("portfolio:skill_create"), {}, follow=True)

        self.assertNotContains(response, "を登録しました。")

    def test_form_has_link_back_to_dashboard(self):
        self.client.login(username="admin", password="password123")
        response = self.client.get(reverse("portfolio:skill_create"))
        self.assertContains(response, f'href="{reverse("portfolio:dashboard")}"')


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

    def test_post_invalid_data_shows_errors(self):
        self.client.login(username="admin", password="password123")

        response = self.client.post(
            reverse("portfolio:skill_update", args=[self.skill.pk]),
            {"name": ""},
        )

        self.assertEqual(response.status_code, 200)
        self.skill.refresh_from_db()
        self.assertEqual(self.skill.name, "既存のスキル")

    def test_unauthenticated_post_is_rejected_and_changes_nothing(self):
        url = reverse("portfolio:skill_update", args=[self.skill.pk])

        response = self.client.post(url, {"name": "不正な更新"})

        self.assertRedirects(response, f"{reverse('portfolio:login')}?next={url}")
        self.skill.refresh_from_db()
        self.assertEqual(self.skill.name, "既存のスキル")

    def test_post_duplicate_name_shows_errors(self):
        Skill.objects.create(name="別のスキル")
        self.client.login(username="admin", password="password123")

        response = self.client.post(
            reverse("portfolio:skill_update", args=[self.skill.pk]), {"name": "別のスキル"}
        )

        self.assertEqual(response.status_code, 200)
        self.skill.refresh_from_db()
        self.assertEqual(self.skill.name, "既存のスキル")

    def test_success_message_is_shown_on_dashboard(self):
        self.client.login(username="admin", password="password123")

        response = self.client.post(
            reverse("portfolio:skill_update", args=[self.skill.pk]), {"name": "更新後"}, follow=True
        )

        self.assertContains(response, "スキルを更新しました。")


class SkillDeleteViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin", password="password123")
        self.skill = Skill.objects.create(name="削除対象のスキル")

    def test_requires_login(self):
        url = reverse("portfolio:skill_delete", args=[self.skill.pk])
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('portfolio:login')}?next={url}")

    def test_get_shows_confirmation(self):
        self.client.login(username="admin", password="password123")
        response = self.client.get(reverse("portfolio:skill_delete", args=[self.skill.pk]))
        self.assertContains(response, "削除対象のスキル")

    def test_post_confirm_yes_deletes_skill(self):
        self.client.login(username="admin", password="password123")

        response = self.client.post(
            reverse("portfolio:skill_delete", args=[self.skill.pk]), {"confirm": "yes"}
        )

        self.assertRedirects(response, reverse("portfolio:dashboard"))
        self.assertEqual(Skill.objects.count(), 0)

    def test_get_with_unknown_pk_returns_404(self):
        self.client.login(username="admin", password="password123")
        response = self.client.get(reverse("portfolio:skill_delete", args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_post_confirm_no_keeps_skill(self):
        self.client.login(username="admin", password="password123")

        response = self.client.post(
            reverse("portfolio:skill_delete", args=[self.skill.pk]), {"confirm": "no"}
        )

        self.assertRedirects(response, reverse("portfolio:dashboard"))
        self.assertEqual(Skill.objects.count(), 1)

    def test_get_does_not_delete(self):
        self.client.login(username="admin", password="password123")
        url = reverse("portfolio:skill_delete", args=[self.skill.pk])

        self.client.get(url)
        self.client.get(url, {"confirm": "yes"})

        self.assertEqual(Skill.objects.count(), 1)

    def test_unauthenticated_post_is_rejected_and_deletes_nothing(self):
        url = reverse("portfolio:skill_delete", args=[self.skill.pk])

        response = self.client.post(url, {"confirm": "yes"})

        self.assertRedirects(response, f"{reverse('portfolio:login')}?next={url}")
        self.assertEqual(Skill.objects.count(), 1)

    def test_post_with_unknown_pk_returns_404(self):
        self.client.login(username="admin", password="password123")
        response = self.client.post(
            reverse("portfolio:skill_delete", args=[9999]), {"confirm": "yes"}
        )
        self.assertEqual(response.status_code, 404)

    def test_post_without_csrf_token_is_forbidden(self):
        client = Client(enforce_csrf_checks=True)
        client.login(username="admin", password="password123")

        response = client.post(
            reverse("portfolio:skill_delete", args=[self.skill.pk]), {"confirm": "yes"}
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Skill.objects.count(), 1)

    def test_success_message_is_shown_on_dashboard(self):
        self.client.login(username="admin", password="password123")

        response = self.client.post(
            reverse("portfolio:skill_delete", args=[self.skill.pk]), {"confirm": "yes"}, follow=True
        )

        self.assertContains(response, "スキルを削除しました。")

    def test_cancel_shows_no_message(self):
        self.client.login(username="admin", password="password123")

        response = self.client.post(
            reverse("portfolio:skill_delete", args=[self.skill.pk]), {"confirm": "no"}, follow=True
        )

        self.assertNotContains(response, "を削除しました。")
