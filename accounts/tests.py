from django.test import TestCase
from django.urls import reverse

from .models import User

PW = "Tut0rMatch#2026"


class AccountFeatureTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user("maria", "maria@cit.edu", PW, role="student", first_name="Maria", last_name="Santos")
        self.tutor = User.objects.create_user("carlo", "carlo@cit.edu", PW, role="tutor", first_name="Carlo", last_name="Reyes")

    def reg(self, **over):
        data = dict(first_name="Ana", last_name="Lim", username="ana", email="ana@cit.edu", role="tutor", password1=PW, password2=PW)
        data.update(over)
        return self.client.post(reverse("register"), data)

    def test_register_hashes_password(self):
        self.assertRedirects(self.reg(), reverse("login"))
        u = User.objects.get(username="ana")
        self.assertNotEqual(u.password, PW)
        self.assertTrue(u.check_password(PW))
        self.assertEqual(u.role, "tutor")

    def test_register_validation(self):
        self.assertContains(self.reg(username="maria"), "already exists")
        self.assertContains(self.reg(email="MARIA@cit.edu"), "already exists")
        self.assertEqual(self.reg(password2="different").status_code, 200)
        self.assertEqual(self.reg(email="not-an-email").status_code, 200)
        self.assertFalse(User.objects.filter(username="ana").exists())

    def test_login_by_username_and_email(self):
        for ident in ("maria", "maria@cit.edu"):
            self.client.logout()
            r = self.client.post(reverse("login"), {"username": ident, "password": PW})
            self.assertRedirects(r, reverse("dashboard"), fetch_redirect_response=False)

    def test_invalid_login_shows_error(self):
        r = self.client.post(reverse("login"), {"username": "maria", "password": "wrong"})
        self.assertContains(r, "Invalid username or password")

    def test_login_required(self):
        for name in ("dashboard", "student_dashboard", "tutor_dashboard", "profile", "profile_edit"):
            r = self.client.get(reverse(name))
            self.assertEqual(r.status_code, 302)
            self.assertIn(reverse("login"), r.url)

    def test_role_dashboards(self):
        self.client.login(username="maria", password=PW)
        self.assertRedirects(self.client.get(reverse("dashboard")), reverse("student_dashboard"))
        self.assertEqual(self.client.get(reverse("tutor_dashboard")).status_code, 403)
        self.client.login(username="carlo", password=PW)
        self.assertRedirects(self.client.get(reverse("dashboard")), reverse("tutor_dashboard"))
        self.assertEqual(self.client.get(reverse("student_dashboard")).status_code, 403)

    def test_profile_update_own_only(self):
        self.client.login(username="maria", password=PW)
        r = self.client.post(reverse("profile_edit"), dict(first_name="Mia", last_name="Santos", email="maria@cit.edu", phone="0917", bio="Hi"))
        self.assertRedirects(r, reverse("profile"))
        self.student.refresh_from_db(); self.tutor.refresh_from_db()
        self.assertEqual(self.student.first_name, "Mia")
        self.assertEqual(self.tutor.first_name, "Carlo")
        self.assertContains(self.client.get(reverse("profile")), "Mia")

    def test_profile_email_must_be_unique(self):
        self.client.login(username="maria", password=PW)
        r = self.client.post(reverse("profile_edit"), dict(first_name="Maria", last_name="S", email="carlo@cit.edu"))
        self.assertContains(r, "already uses this email")

    def test_logout_ends_session(self):
        self.client.login(username="maria", password=PW)
        self.client.post(reverse("logout"))
        self.assertEqual(self.client.get(reverse("profile")).status_code, 302)
