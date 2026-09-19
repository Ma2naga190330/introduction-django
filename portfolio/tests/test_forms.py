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
