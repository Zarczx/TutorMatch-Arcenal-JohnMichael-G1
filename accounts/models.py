from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        TUTOR = "tutor", "Tutor"

    class YearLevel(models.TextChoices):
        Y1 = "1", "1st year"
        Y2 = "2", "2nd year"
        Y3 = "3", "3rd year"
        Y4 = "4", "4th year"
        OTHER = "other", "Other"

    email = models.EmailField("email address", unique=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)
    phone = models.CharField("contact number", max_length=20, blank=True)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to="profiles/", blank=True)
    subjects = models.CharField(max_length=255, blank=True, help_text="Comma-separated")
    hourly_rate = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    year_level = models.CharField(max_length=10, choices=YearLevel.choices, blank=True)
    availability = models.CharField(max_length=255, blank=True, help_text="e.g. Mon 2-5pm, Sat 9am-12pm")
    onboarded = models.BooleanField(default=False)

    @property
    def initials(self):
        return ((self.first_name[:1] + self.last_name[:1]) or self.username[:2]).upper()

    @property
    def full_name(self):
        return self.get_full_name() or self.username

    @property
    def checklist(self):
        """Returns the profile steps and whether each one is done."""
        if self.role == self.Role.TUTOR:
            items = [
                ("Add your subjects", bool(self.subjects), "accounts:onboarding"),
                ("Set your availability", bool(self.availability), "accounts:onboarding"),
                ("Set your hourly rate", self.hourly_rate is not None, "accounts:onboarding"),
                ("Add a bio", bool(self.bio), "profile_edit"),
            ]
        else:
            items = [
                ("Tell us what you need help with", bool(self.subjects), "accounts:onboarding"),
                ("Add your year level", bool(self.year_level), "accounts:onboarding"),
                ("Add a bio", bool(self.bio), "profile_edit"),
            ]
        return items

    @property
    def progress(self):
        items = self.checklist
        done = sum(1 for _, ok, _ in items if ok)
        return int(done * 100 / len(items))