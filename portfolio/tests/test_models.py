from django.db.utils import IntegrityError
from django.test import TestCase

from portfolio.models import Activity, Certification, Skill, Tag


class TagModelTest(TestCase):
    def test_str_returns_name(self):
        tag = Tag.objects.create(name="Winner")
        self.assertEqual(str(tag), "Winner")

    def test_name_must_be_unique(self):
        from django.db.utils import IntegrityError

        Tag.objects.create(name="Winner")
        with self.assertRaises(IntegrityError):
            Tag.objects.create(name="Winner")


class ActivityModelTest(TestCase):
    def test_str_returns_title(self):
        activity = Activity.objects.create(icon="trophy", title="北九州Techハッカソン2025")
        self.assertEqual(str(activity), "北九州Techハッカソン2025")

    def test_can_attach_multiple_tags(self):
        activity = Activity.objects.create(icon="rocket", title="Startup Weekend 北九州")
        winner = Tag.objects.create(name="Winner")
        organizer = Tag.objects.create(name="organizer")
        activity.tags.set([winner, organizer])
        self.assertEqual(list(activity.tags.order_by("name")), [winner, organizer])

    def test_ordered_by_created_at(self):
        first = Activity.objects.create(icon="trophy", title="先に登録した実績")
        second = Activity.objects.create(icon="rocket", title="後に登録した実績")
        self.assertEqual(list(Activity.objects.all()), [first, second])


class CertificationModelTest(TestCase):
    def test_str_returns_title(self):
        certification = Certification.objects.create(icon="shield-check", title="基本情報技術者試験")
        self.assertEqual(str(certification), "基本情報技術者試験")

    def test_ordered_by_created_at(self):
        first = Certification.objects.create(icon="shield-check", title="基本情報技術者試験")
        second = Certification.objects.create(icon="files", title="簿記実務検定2級")
        self.assertEqual(list(Certification.objects.all()), [first, second])


class SkillModelTest(TestCase):
    def test_str_returns_name(self):
        skill = Skill.objects.create(name="Python / Django")
        self.assertEqual(str(skill), "Python / Django")

    def test_name_must_be_unique(self):
        Skill.objects.create(name="Python / Django")
        with self.assertRaises(IntegrityError):
            Skill.objects.create(name="Python / Django")

    def test_ordered_by_created_at(self):
        first = Skill.objects.create(name="HTML5 / CSS3")
        second = Skill.objects.create(name="Go")
        self.assertEqual(list(Skill.objects.all()), [first, second])
