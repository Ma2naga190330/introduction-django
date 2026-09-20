from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from portfolio.models import Activity, Tag


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

    def test_unauthenticated_post_is_rejected_and_creates_nothing(self):
        url = reverse("portfolio:activity_create")

        response = self.client.post(url, {"icon": "trophy", "title": "不正な登録", "tags": ""})

        self.assertRedirects(response, f"{reverse('portfolio:login')}?next={url}")
        self.assertEqual(Activity.objects.count(), 0)


class ActivityUpdateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin", password="password123")
        self.activity = Activity.objects.create(icon="trophy", title="既存の実績")

    def test_requires_login(self):
        url = reverse("portfolio:activity_update", args=[self.activity.pk])
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('portfolio:login')}?next={url}")

    def test_get_prefills_existing_data(self):
        self.client.login(username="admin", password="password123")
        response = self.client.get(reverse("portfolio:activity_update", args=[self.activity.pk]))
        self.assertContains(response, "既存の実績")

    def test_post_valid_data_updates_activity(self):
        self.client.login(username="admin", password="password123")

        response = self.client.post(
            reverse("portfolio:activity_update", args=[self.activity.pk]),
            {"icon": "trophy", "title": "更新後の実績", "tags": ""},
        )

        self.assertRedirects(response, reverse("portfolio:dashboard"))
        self.activity.refresh_from_db()
        self.assertEqual(self.activity.title, "更新後の実績")

    def test_get_with_unknown_pk_returns_404(self):
        self.client.login(username="admin", password="password123")
        response = self.client.get(reverse("portfolio:activity_update", args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_post_invalid_data_shows_errors(self):
        self.client.login(username="admin", password="password123")

        response = self.client.post(
            reverse("portfolio:activity_update", args=[self.activity.pk]),
            {"icon": "trophy", "title": "", "tags": ""},
        )

        self.assertEqual(response.status_code, 200)
        self.activity.refresh_from_db()
        self.assertEqual(self.activity.title, "既存の実績")

    def test_unauthenticated_post_is_rejected_and_changes_nothing(self):
        url = reverse("portfolio:activity_update", args=[self.activity.pk])

        response = self.client.post(url, {"icon": "trophy", "title": "不正な更新", "tags": ""})

        self.assertRedirects(response, f"{reverse('portfolio:login')}?next={url}")
        self.activity.refresh_from_db()
        self.assertEqual(self.activity.title, "既存の実績")

    def test_post_replaces_tags_and_removes_dropped_ones(self):
        self.activity.tags.set(
            [Tag.objects.create(name="Winner"), Tag.objects.create(name="organizer")]
        )
        self.client.login(username="admin", password="password123")

        self.client.post(
            reverse("portfolio:activity_update", args=[self.activity.pk]),
            {"icon": "trophy", "title": "既存の実績", "tags": "organizer, mentor"},
        )

        self.assertEqual(
            sorted(self.activity.tags.values_list("name", flat=True)), ["mentor", "organizer"]
        )

    def test_post_with_empty_tags_removes_all_tags(self):
        self.activity.tags.set([Tag.objects.create(name="Winner")])
        self.client.login(username="admin", password="password123")

        self.client.post(
            reverse("portfolio:activity_update", args=[self.activity.pk]),
            {"icon": "trophy", "title": "既存の実績", "tags": ""},
        )

        self.assertEqual(self.activity.tags.count(), 0)


class ActivityDeleteViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin", password="password123")
        self.activity = Activity.objects.create(icon="trophy", title="削除対象の実績")

    def test_requires_login(self):
        url = reverse("portfolio:activity_delete", args=[self.activity.pk])
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('portfolio:login')}?next={url}")

    def test_get_shows_confirmation(self):
        self.client.login(username="admin", password="password123")
        response = self.client.get(reverse("portfolio:activity_delete", args=[self.activity.pk]))
        self.assertContains(response, "削除対象の実績")

    def test_post_confirm_yes_deletes_activity(self):
        self.client.login(username="admin", password="password123")

        response = self.client.post(
            reverse("portfolio:activity_delete", args=[self.activity.pk]), {"confirm": "yes"}
        )

        self.assertRedirects(response, reverse("portfolio:dashboard"))
        self.assertEqual(Activity.objects.count(), 0)

    def test_post_confirm_no_keeps_activity(self):
        self.client.login(username="admin", password="password123")

        response = self.client.post(
            reverse("portfolio:activity_delete", args=[self.activity.pk]), {"confirm": "no"}
        )

        self.assertRedirects(response, reverse("portfolio:dashboard"))
        self.assertEqual(Activity.objects.count(), 1)

    def test_get_with_unknown_pk_returns_404(self):
        self.client.login(username="admin", password="password123")
        response = self.client.get(reverse("portfolio:activity_delete", args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_get_does_not_delete(self):
        self.client.login(username="admin", password="password123")
        url = reverse("portfolio:activity_delete", args=[self.activity.pk])

        self.client.get(url)
        self.client.get(url, {"confirm": "yes"})

        self.assertEqual(Activity.objects.count(), 1)

    def test_unauthenticated_post_is_rejected_and_deletes_nothing(self):
        url = reverse("portfolio:activity_delete", args=[self.activity.pk])

        response = self.client.post(url, {"confirm": "yes"})

        self.assertRedirects(response, f"{reverse('portfolio:login')}?next={url}")
        self.assertEqual(Activity.objects.count(), 1)

    def test_post_with_unknown_pk_returns_404(self):
        self.client.login(username="admin", password="password123")
        response = self.client.post(
            reverse("portfolio:activity_delete", args=[9999]), {"confirm": "yes"}
        )
        self.assertEqual(response.status_code, 404)

    def test_post_without_csrf_token_is_forbidden(self):
        client = Client(enforce_csrf_checks=True)
        client.login(username="admin", password="password123")

        response = client.post(
            reverse("portfolio:activity_delete", args=[self.activity.pk]), {"confirm": "yes"}
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Activity.objects.count(), 1)
