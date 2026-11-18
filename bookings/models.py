from datetime import datetime, timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class Booking(models.Model):
    """A session request from a student to a tutor for one subject."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        DECLINED = "declined", "Declined"
        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"

    DURATIONS = [(60, "1 hour"), (90, "1.5 hours"), (120, "2 hours")]

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings_made")
    tutor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings_received",
                              limit_choices_to={"role": "tutor"})
    subject = models.ForeignKey("directory.Subject", on_delete=models.PROTECT, related_name="bookings")
    date = models.DateField()
    start_time = models.TimeField()
    duration = models.PositiveSmallIntegerField(choices=DURATIONS, default=60)
    notes = models.TextField(blank=True, max_length=500)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["date", "start_time"]

    def __str__(self):
        return f"{self.subject} · {self.student} → {self.tutor} ({self.date})"

    @property
    def start_dt(self):
        return datetime.combine(self.date, self.start_time)

    @property
    def end_dt(self):
        return self.start_dt + timedelta(minutes=self.duration)

    @property
    def end_time(self):
        return self.end_dt.time()

    # What the owner may still do, depending on status
    @property
    def can_edit(self):
        return self.status == self.Status.PENDING

    @property
    def can_cancel(self):
        return self.status in (self.Status.PENDING, self.Status.CONFIRMED)

    @property
    def can_delete(self):
        return self.status in (self.Status.PENDING, self.Status.DECLINED, self.Status.CANCELLED)

    @property
    def can_complete(self):
        return self.status == self.Status.CONFIRMED and self.date <= timezone.localdate()


def overlapping(queryset, day, start, minutes, exclude_pk=None):
    """Bookings in `queryset` that overlap the given time slot."""
    new_start = datetime.combine(day, start)
    new_end = new_start + timedelta(minutes=minutes)
    return [b for b in queryset.filter(date=day).exclude(pk=exclude_pk)
            if b.start_dt < new_end and new_start < b.end_dt]