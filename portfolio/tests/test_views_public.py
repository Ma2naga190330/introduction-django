from django.test import TestCase
from django.urls import reverse

from portfolio.models import Activity, Certification, Skill, Tag


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
        self.assertContains(response, "登録された資格情報はまだありません。")
        self.assertContains(response, "登録されたスキルはまだありません。")

    def test_shows_tags_of_each_activity(self):
        activity = Activity.objects.create(icon="rocket", title="Startup Weekend 北九州")
        activity.tags.set([Tag.objects.create(name="Winner"), Tag.objects.create(name="organizer")])

        response = self.client.get(reverse("portfolio:profile"))

        self.assertContains(response, '<span class="tag">Winner</span>', html=True)
        self.assertContains(response, '<span class="tag">organizer</span>', html=True)

    def test_lists_items_in_registration_order(self):
        Activity.objects.create(icon="trophy", title="先に登録した実績")
        Activity.objects.create(icon="rocket", title="後に登録した実績")
        Certification.objects.create(icon="shield-check", title="先の資格")
        Certification.objects.create(icon="files", title="後の資格")
        Skill.objects.create(name="先のスキル")
        Skill.objects.create(name="後のスキル")

        response = self.client.get(reverse("portfolio:profile"))

        self.assertEqual(
            [a.title for a in response.context["activities"]], ["先に登録した実績", "後に登録した実績"]
        )
        self.assertEqual(
            [c.title for c in response.context["certifications"]], ["先の資格", "後の資格"]
        )
        self.assertEqual([s.name for s in response.context["skills"]], ["先のスキル", "後のスキル"])

    def test_query_count_does_not_grow_with_number_of_tagged_activities(self):
        def add_tagged_activity(n):
            activity = Activity.objects.create(icon="trophy", title=f"実績{n}")
            activity.tags.set([Tag.objects.create(name=f"tag{n}a"), Tag.objects.create(name=f"tag{n}b")])

        add_tagged_activity(0)
        with self.assertNumQueries(4):
            self.client.get(reverse("portfolio:profile"))

        for n in range(1, 6):
            add_tagged_activity(n)
        with self.assertNumQueries(4):
            self.client.get(reverse("portfolio:profile"))

    def test_external_links_are_safe(self):
        response = self.client.get(reverse("portfolio:profile"))
        content = response.content.decode()

        self.assertNotIn('href="mailto:ktq2590310@stu.o-hara.ac.jp" target', content)
        self.assertEqual(content.count('target="_blank"'), content.count('rel="noopener noreferrer"'))

    def test_loads_own_css_and_js(self):
        response = self.client.get(reverse("portfolio:profile"))

        self.assertContains(response, "portfolio/css/style.css")
        self.assertContains(response, "portfolio/js/main.js")

    def test_renders_lucide_icon_for_each_activity_and_certification(self):
        Activity.objects.create(icon="trophy", title="北九州Techハッカソン2025")
        Certification.objects.create(icon="shield-check", title="基本情報技術者試験")

        response = self.client.get(reverse("portfolio:profile"))

        self.assertContains(response, '<i data-lucide="trophy">', count=1)
        self.assertContains(response, '<i data-lucide="shield-check">', count=1)
