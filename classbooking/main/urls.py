from django.urls import path
from . import views

urlpatterns = [
    path("overview/", views.overview, name="overview"),
    path("classroom/", views.classroom, name="classroom"),
    path("booking/", views.booking, name="booking"),
    path("booking/<int:pk>/edit/", views.booking_edit, name="booking_edit"),
    path("booking/<int:pk>/cancel/", views.booking_cancel, name="booking_cancel"),
    path("classroom/add/", views.classroom_add, name="classroom_add"),
    path("classroom/<int:pk>/edit/", views.classroom_edit, name="classroom_edit"),
    path("classroom/<int:pk>/delete/", views.classroom_delete, name="classroom_delete"),
]
