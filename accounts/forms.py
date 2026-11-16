from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User


class RegisterForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.Role.choices, widget=forms.RadioSelect, initial=User.Role.STUDENT)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("first_name", "last_name", "username", "email", "role")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("first_name", "last_name", "email"):
            self.fields[name].required = True
        self.fields["email"].widget.attrs["placeholder"] = "name@cit.edu"
        self.fields["email"].label = "CIT-U email"
        self.fields["password1"].help_text = ""
        self.fields["password2"].help_text = ""
        self.fields["password2"].label = "Confirm password"

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Username or email"
        self.fields["username"].widget.attrs.update({"placeholder": "maria or maria@cit.edu", "autofocus": True})
        self.fields["password"].widget.attrs["placeholder"] = "Your password"


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "phone", "bio", "photo", "subjects", "hourly_rate")
        widgets = {"bio": forms.Textarea(attrs={"rows": 3})}
        labels = {"hourly_rate": "Rate per hour (₱)", "subjects": "Subjects (comma-separated)"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        if self.instance.role != User.Role.TUTOR:
            del self.fields["subjects"], self.fields["hourly_rate"]

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Another account already uses this email.")
        return email

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if photo and hasattr(photo, "size") and photo.size > 2 * 1024 * 1024:
            raise forms.ValidationError("Photo must be 2 MB or smaller.")
        return photo
