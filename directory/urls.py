from django.urls import path

from . import views

urlpatterns = [
    path("tutors/", views.tutor_list, name="tutor_list"),
    path("my-subjects/", views.my_subjects, name="my_subjects"),
]