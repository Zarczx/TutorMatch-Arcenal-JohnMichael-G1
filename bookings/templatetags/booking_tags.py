from django import template
from django.utils import timezone

register = template.Library()


@register.inclusion_tag("bookings/_summary.html", takes_context=True)
def booking_summary(context):
    """Real booking numbers and upcoming sessions for the dashboard."""
    user = context["request"].user
    is_tutor = user.role == "tutor"
    qs = (user.bookings_received if is_tutor else user.bookings_made).select_related("student", "tutor", "subject")
    today = timezone.localdate()
    return {
        "is_tutor": is_tutor,
        "stats": {
            "pending": qs.filter(status="pending").count(),
            "upcoming": qs.filter(status="confirmed", date__gte=today).count(),
            "completed": qs.filter(status="completed").count(),
        },
        "upcoming": qs.filter(status__in=["pending", "confirmed"], date__gte=today).order_by("date", "start_time")[:5],
    }