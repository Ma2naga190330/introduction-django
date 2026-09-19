from django.test import TestCase

from portfolio.models import Tag


class TagModelTest(TestCase):
    def test_str_returns_name(self):
        tag = Tag.objects.create(name="Winner")
        self.assertEqual(str(tag), "Winner")

    def test_name_must_be_unique(self):
        from django.db.utils import IntegrityError

        Tag.objects.create(name="Winner")
        with self.assertRaises(IntegrityError):
            Tag.objects.create(name="Winner")
