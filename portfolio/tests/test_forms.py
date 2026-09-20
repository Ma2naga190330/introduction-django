from unittest import mock

from django.test import TestCase

from portfolio.forms import ActivityForm
from portfolio.models import Activity, Tag


class ActivityFormTest(TestCase):
    def test_valid_with_required_fields(self):
        form = ActivityForm(data={"icon": "trophy", "title": "北九州Techハッカソン2025", "tags": ""})
        self.assertTrue(form.is_valid())

    def test_invalid_without_title(self):
        form = ActivityForm(data={"icon": "trophy", "title": "", "tags": ""})
        self.assertFalse(form.is_valid())

    def test_save_creates_tags_from_comma_separated_input(self):
        form = ActivityForm(
            data={"icon": "trophy", "title": "Startup Weekend 北九州", "tags": "Winner, organizer"}
        )
        self.assertTrue(form.is_valid())

        activity = form.save()

        self.assertEqual(
            sorted(activity.tags.values_list("name", flat=True)), ["Winner", "organizer"]
        )

    def test_editing_prefills_existing_tags(self):
        activity = Activity.objects.create(icon="trophy", title="既存の実績")
        activity.tags.set([Tag.objects.create(name="Winner")])

        form = ActivityForm(instance=activity)

        self.assertEqual(form.fields["tags"].initial, "Winner")

    def _form(self, tags, **kwargs):
        return ActivityForm(data={"icon": "trophy", "title": "実績", "tags": tags}, **kwargs)

    def test_full_width_comma_and_ideographic_comma_split_tags(self):
        form = self._form("Winner，organizer、mentor")
        self.assertTrue(form.is_valid())

        activity = form.save()

        self.assertEqual(
            sorted(activity.tags.values_list("name", flat=True)),
            ["Winner", "mentor", "organizer"],
        )

    def test_blank_entries_are_ignored(self):
        form = self._form(" , ,")
        self.assertTrue(form.is_valid())

        activity = form.save()

        self.assertEqual(activity.tags.count(), 0)
        self.assertEqual(Tag.objects.count(), 0)

    def test_duplicate_names_in_one_submission_create_one_tag(self):
        form = self._form("Winner, Winner,Winner")
        self.assertTrue(form.is_valid())

        activity = form.save()

        self.assertEqual(list(activity.tags.values_list("name", flat=True)), ["Winner"])
        self.assertEqual(Tag.objects.count(), 1)

    def test_clean_tags_keeps_first_seen_order_without_duplicates(self):
        form = self._form("b, a, b, c")
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["tags"], ["b", "a", "c"])

    def test_existing_tag_is_reused_not_duplicated(self):
        existing = Tag.objects.create(name="Winner")

        activity = self._form("Winner").save()

        self.assertEqual(Tag.objects.count(), 1)
        self.assertEqual(list(activity.tags.all()), [existing])

    def test_tag_longer_than_max_length_is_rejected(self):
        max_length = Tag._meta.get_field("name").max_length

        form = self._form("a" * (max_length + 1))

        self.assertFalse(form.is_valid())
        self.assertIn("tags", form.errors)

    def test_tag_of_max_length_is_accepted(self):
        max_length = Tag._meta.get_field("name").max_length
        self.assertTrue(self._form("a" * max_length).is_valid())

    def test_editing_removes_tags_dropped_from_input(self):
        activity = Activity.objects.create(icon="trophy", title="既存の実績")
        activity.tags.set([Tag.objects.create(name="Winner"), Tag.objects.create(name="organizer")])

        form = self._form("organizer", instance=activity)
        self.assertTrue(form.is_valid())
        form.save()

        self.assertEqual(list(activity.tags.values_list("name", flat=True)), ["organizer"])

    def test_editing_with_empty_tags_clears_all_tags(self):
        activity = Activity.objects.create(icon="trophy", title="既存の実績")
        activity.tags.set([Tag.objects.create(name="Winner")])

        form = self._form("", instance=activity)
        self.assertTrue(form.is_valid())
        form.save()

        self.assertEqual(activity.tags.count(), 0)

    def test_save_commit_false_applies_tags_on_save_m2m(self):
        form = self._form("Winner, organizer")
        self.assertTrue(form.is_valid())

        activity = form.save(commit=False)
        self.assertIsNone(activity.pk)
        activity.save()
        form.save_m2m()

        self.assertEqual(
            sorted(activity.tags.values_list("name", flat=True)), ["Winner", "organizer"]
        )

    def test_failure_while_applying_tags_rolls_back_the_activity(self):
        form = self._form("Winner")
        self.assertTrue(form.is_valid())

        with mock.patch.object(Tag.objects, "get_or_create", side_effect=RuntimeError("boom")):
            with self.assertRaises(RuntimeError):
                form.save()

        self.assertEqual(Activity.objects.count(), 0)
