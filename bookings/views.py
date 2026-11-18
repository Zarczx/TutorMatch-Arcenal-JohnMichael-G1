from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.decorators import role_required
from accounts.models import User

from .forms import BookingForm
from .models import Booking, overlapping

S = Booking.Status


@role_required("student")
def booking_create(request, tutor_id):
    """CREATE: a student requests a session with a tutor."""
    tutor = get_object_or_404(User, pk=tutor_id, role="tutor", is_active=True)
    if not tutor.teaches.exists():
        messages.error(request, "This tutor hasn’t listed any subjects yet.")
        return redirect("tutor_list")
    initial = {"subject": request.GET.get("subject")} if request.GET.get("subject", "").isdigit() else {}
    form = BookingForm(request.POST or None, tutor=tutor, student=request.user, initial=initial)
    if request.method == "POST":
        if form.is_valid():
            booking = form.save(commit=False)
            booking.student, booking.tutor = request.user, tutor
            booking.save()
            messages.success(request, f"Request sent to {tutor.full_name}. You’ll see their reply here.")
            return redirect("booking_list")
        messages.error(request, "Please fix the highlighted fields.")
    return render(request, "bookings/booking_form.html", {"form": form, "tutor": tutor, "heading": "Book a session"})


@login_required
def booking_list(request):
    """READ: students see their requests; tutors see requests sent to them."""
    user = request.user
    if user.role == "tutor":
        qs = user.bookings_received.select_related("student", "subject")
    else:
        qs = user.bookings_made.select_related("tutor", "subject")
    status = request.GET.get("status", "")
    if status in S.values:
        qs = qs.filter(status=status)
    return render(request, "bookings/booking_list.html",
                  {"bookings": qs, "status": status, "statuses": S.choices})


@role_required("student")
def booking_update(request, pk):
    """UPDATE: a student edits a request that is still pending."""
    booking = get_object_or_404(Booking, pk=pk, student=request.user)
    if not booking.can_edit:
        messages.error(request, "Only pending requests can be edited.")
        return redirect("booking_list")
    form = BookingForm(request.POST or None, instance=booking, tutor=booking.tutor, student=request.user)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Booking updated.")
            return redirect("booking_list")
        messages.error(request, "Please fix the highlighted fields.")
    return render(request, "bookings/booking_form.html",
                  {"form": form, "tutor": booking.tutor, "heading": "Edit booking", "booking": booking})


@role_required("student")
@require_POST
def booking_cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk, student=request.user)
    if booking.can_cancel:
        booking.status = S.CANCELLED
        booking.save(update_fields=["status", "updated_at"])
        messages.success(request, "Booking cancelled.")
    else:
        messages.error(request, "This booking can’t be cancelled.")
    return redirect("booking_list")


@role_required("student")
def booking_delete(request, pk):
    """DELETE: a student removes a pending, declined, or cancelled booking."""
    booking = get_object_or_404(Booking, pk=pk, student=request.user)
    if not booking.can_delete:
        messages.error(request, "Cancel this booking first, then you can delete it.")
        return redirect("booking_list")
    if request.method == "POST":
        booking.delete()
        messages.success(request, "Booking deleted.")
        return redirect("booking_list")
    return render(request, "bookings/booking_confirm_delete.html", {"booking": booking})


@role_required("tutor")
@require_POST
def booking_respond(request, pk):
    """A tutor confirms or declines a pending request sent to them."""
    booking = get_object_or_404(Booking, pk=pk, tutor=request.user)
    action = request.POST.get("action")
    if booking.status != S.PENDING:
        messages.error(request, "This request has already been answered.")
    elif action == "confirm":
        if overlapping(Booking.objects.filter(tutor=request.user, status=S.CONFIRMED),
                       booking.date, booking.start_time, booking.duration, booking.pk):
            messages.error(request, "You already have a confirmed session at that time.")
        else:
            booking.status = S.CONFIRMED
            booking.save(update_fields=["status", "updated_at"])
            messages.success(request, "Booking confirmed.")
    elif action == "decline":
        booking.status = S.DECLINED
        booking.save(update_fields=["status", "updated_at"])
        messages.success(request, "Booking declined.")
    else:
        messages.error(request, "Unknown action.")
    return redirect("booking_list")


@role_required("tutor")
@require_POST
def booking_complete(request, pk):
    booking = get_object_or_404(Booking, pk=pk, tutor=request.user)
    if booking.can_complete:
        booking.status = S.COMPLETED
        booking.save(update_fields=["status", "updated_at"])
        messages.success(request, "Session marked as completed.")
    else:
        messages.error(request, "Only confirmed sessions that have started can be completed.")
    return redirect("booking_list")