from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class TutorMatchUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "is_staff")
    list_filter = ("role", "is_staff", "is_active")
    fieldsets = UserAdmin.fieldsets + (("TutorMatch", {"fields": ("role", "phone", "bio", "photo", "subjects", "hourly_rate")}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("TutorMatch", {"fields": ("email", "role")}),)
