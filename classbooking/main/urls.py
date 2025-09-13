from django.urls import path
from . import views

urlpatterns = [
    path("overview/", views.overview, name="overview"),
    path("classrooms/", views.classroom, name="classroom"),
    path("booking/", views.booking, name="booking"),
    path("booking/<int:pk>/edit/", views.booking_edit, name="booking_edit"),
    path("booking/<int:pk>/cancel/", views.booking_cancel, name="booking_cancel"),
]
