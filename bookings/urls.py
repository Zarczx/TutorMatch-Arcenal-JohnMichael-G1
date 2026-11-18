from django.urls import path

from . import views

urlpatterns = [
    path("bookings/", views.booking_list, name="booking_list"),
    path("bookings/new/<int:tutor_id>/", views.booking_create, name="booking_create"),
    path("bookings/<int:pk>/edit/", views.booking_update, name="booking_update"),
    path("bookings/<int:pk>/cancel/", views.booking_cancel, name="booking_cancel"),
    path("bookings/<int:pk>/delete/", views.booking_delete, name="booking_delete"),
    path("bookings/<int:pk>/respond/", views.booking_respond, name="booking_respond"),
    path("bookings/<int:pk>/complete/", views.booking_complete, name="booking_complete"),
]