from django.urls import path
from . import views

urlpatterns = [
    path("overview/", views.overview, name="overview"),
    path("classrooms/", views.classroom_list, name="classroom"),
    path("booking/", views.booking, name="booking"),
]
