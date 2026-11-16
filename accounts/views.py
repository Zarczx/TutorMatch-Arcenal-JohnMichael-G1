from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .decorators import role_required
from .forms import LoginForm, ProfileForm, RegisterForm
from .models import User


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    role = request.GET.get("role")
    initial = {"role": role if role in User.Role.values else User.Role.STUDENT}
    form = RegisterForm(request.POST or None, initial=initial)
    if request.method == "POST":
        if form.is_valid():
            form.save()  # password is hashed by Django's auth system
            messages.success(request, "Account created. You can now log in.")
            return redirect("login")
        messages.error(request, "Please fix the highlighted fields.")
    return render(request, "accounts/register.html", {"form": form})


class LoginView(auth_views.LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def dispatch(self, request, *args, **kwargs):
        if request.method == "GET" and request.GET.get("next") and not request.user.is_authenticated:
            messages.error(request, "Please log in to view that page.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, f"Welcome back, {form.get_user().first_name or form.get_user().username}!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password. Check your details and try again.")
        return super().form_invalid(form)


@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")


@login_required
def dashboard(request):
    """Send each user to the dashboard for their role."""
    return redirect("tutor_dashboard" if request.user.role == User.Role.TUTOR else "student_dashboard")


@role_required(User.Role.STUDENT)
def student_dashboard(request):
    return render(request, "accounts/dashboard_student.html")


@role_required(User.Role.TUTOR)
def tutor_dashboard(request):
    return render(request, "accounts/dashboard_tutor.html")


@login_required
def profile(request):
    return render(request, "accounts/profile.html")  # always the logged-in user's own profile


@login_required
def profile_edit(request):
    user = User.objects.get(pk=request.user.pk)  # only ever edits the current user
    form = ProfileForm(request.POST or None, request.FILES or None, instance=user)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("profile")
        messages.error(request, "Please fix the highlighted fields.")
    return render(request, "accounts/profile_edit.html", {"form": form})
