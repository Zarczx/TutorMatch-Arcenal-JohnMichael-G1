from django.contrib import messages
from django.db.models import F, Q
from django.shortcuts import redirect, render

from accounts.decorators import role_required
from accounts.models import User

from .forms import TutorSubjectsForm
from .models import Subject


@role_required("student")
def tutor_list(request):
    """Students search tutors by subject or keyword and sort the results."""
    q = request.GET.get("q", "").strip()
    subject_id = request.GET.get("subject", "")
    sort = request.GET.get("sort", "name")
    tutors = User.objects.filter(role="tutor", is_active=True).prefetch_related("teaches")
    if subject_id.isdigit():
        tutors = tutors.filter(teaches__pk=int(subject_id))
    if q:
        tutors = tutors.filter(
            Q(first_name__icontains=q) | Q(last_name__icontains=q)
            | Q(bio__icontains=q) | Q(teaches__name__icontains=q)
        )
    tutors = tutors.distinct()
    if sort == "rate":
        tutors = tutors.order_by(F("hourly_rate").asc(nulls_last=True), "first_name")
    else:
        tutors = tutors.order_by("first_name", "last_name")
    return render(request, "directory/tutor_list.html", {
        "tutors": tutors, "subjects": Subject.objects.all(),
        "q": q, "subject_id": subject_id, "sort": sort,
    })


@role_required("tutor")
def my_subjects(request):
    """Tutors choose which subjects they teach."""
    form = TutorSubjectsForm(request.POST or None, user=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your subjects were updated.")
        return redirect("my_subjects")
    return render(request, "directory/my_subjects.html", {"form": form})