import re

from django import forms
from django.db import transaction

from .models import Activity, Certification, Skill, Tag


class ActivityForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        label="タグ（カンマ区切り）",
        help_text="複数のタグはカンマで区切って入力してください（例: Winner, organizer）",
    )

    class Meta:
        model = Activity
        fields = ["icon", "title"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["tags"].initial = ", ".join(
                self.instance.tags.values_list("name", flat=True)
            )

    def clean_tags(self):
        raw = self.cleaned_data.get("tags", "")
        names = list(dict.fromkeys(n.strip() for n in re.split(r"[,，、]", raw) if n.strip()))
        max_length = Tag._meta.get_field("name").max_length
        too_long = [name for name in names if len(name) > max_length]
        if too_long:
            raise forms.ValidationError(
                f"タグは{max_length}文字以内で入力してください: {', '.join(too_long)}"
            )
        return names

    def save(self, commit=True):
        with transaction.atomic():
            return super().save(commit=commit)

    def _save_m2m(self):
        super()._save_m2m()
        names = self.cleaned_data["tags"]
        tags = [Tag.objects.get_or_create(name=name)[0] for name in names]
        self.instance.tags.set(tags)


class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ["icon", "title"]


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ["name"]
