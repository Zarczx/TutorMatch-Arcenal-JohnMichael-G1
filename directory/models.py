from django.conf import settings
from django.db import models


class Subject(models.Model):
    """A subject that tutors can teach. Many tutors <-> many subjects."""
    name = models.CharField(max_length=80, unique=True)
    tutors = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="teaches", blank=True,
        limit_choices_to={"role": "tutor"},
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name