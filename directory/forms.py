from django import forms

from .models import Subject


class TutorSubjectsForm(forms.Form):
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(), widget=forms.CheckboxSelectMultiple,
        required=False, label="",
    )

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields["subjects"].initial = list(user.teaches.values_list("pk", flat=True))

    def save(self):
        self.user.teaches.set(self.cleaned_data["subjects"])