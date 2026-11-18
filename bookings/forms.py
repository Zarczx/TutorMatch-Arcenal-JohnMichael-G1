from datetime import time

from django import forms
from django.utils import timezone

from .models import Booking, overlapping


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ("subject", "date", "start_time", "duration", "notes")
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "start_time": forms.TimeInput(attrs={"type": "time"}, format="%H:%M"),
            "notes": forms.Textarea(attrs={"rows": 3, "placeholder": "What do you need help with?"}),
        }

    def __init__(self, *args, tutor, student, **kwargs):
        super().__init__(*args, **kwargs)
        self.tutor, self.student = tutor, student
        self.fields["subject"].queryset = tutor.teaches.all()  # only subjects this tutor teaches
        self.fields["subject"].empty_label = "Choose a subject"

    def clean_date(self):
        day = self.cleaned_data["date"]
        if day < timezone.localdate():
            raise forms.ValidationError("The date can’t be in the past.")
        return day

    def clean(self):
        data = super().clean()
        day, start, minutes = data.get("date"), data.get("start_time"), data.get("duration")
        if not (day and start and minutes):
            return data
        now = timezone.localtime()
        if not time(7, 0) <= start <= time(20, 0):
            self.add_error("start_time", "Sessions can start between 7:00 AM and 8:00 PM.")
        elif day == now.date() and start <= now.time():
            self.add_error("start_time", "The start time must be in the future.")
        elif overlapping(Booking.objects.filter(tutor=self.tutor, status=Booking.Status.CONFIRMED),
                         day, start, minutes, self.instance.pk):
            raise forms.ValidationError("This tutor already has a confirmed session at that time.")
        elif overlapping(Booking.objects.filter(student=self.student,
                         status__in=[Booking.Status.PENDING, Booking.Status.CONFIRMED]),
                         day, start, minutes, self.instance.pk):
            raise forms.ValidationError("You already have a booking at that time.")
        return data