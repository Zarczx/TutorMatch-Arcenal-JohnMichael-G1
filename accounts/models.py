from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        TUTOR = "tutor", "Tutor"

    email = models.EmailField("email address", unique=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)
    phone = models.CharField("contact number", max_length=20, blank=True)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to="profiles/", blank=True)
    subjects = models.CharField(max_length=255, blank=True, help_text="Comma-separated (tutors only)")
    hourly_rate = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)

    @property
    def initials(self):
        return ((self.first_name[:1] + self.last_name[:1]) or self.username[:2]).upper()

    @property
    def full_name(self):
        return self.get_full_name() or self.username
