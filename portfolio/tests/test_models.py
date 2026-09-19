from django.test import TestCase

from portfolio.models import Activity, Tag


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
