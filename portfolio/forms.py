from django import forms

from .models import Activity, Certification, Tag


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
        return [name.strip() for name in raw.split(",") if name.strip()]

    def save(self, commit=True):
        activity = super().save(commit=commit)
        if commit:
            self._apply_tags(activity)
        return activity

    def _apply_tags(self, activity):
        names = self.cleaned_data.get("tags", [])
        tags = [Tag.objects.get_or_create(name=name)[0] for name in names]
        activity.tags.set(tags)


class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ["icon", "title"]
