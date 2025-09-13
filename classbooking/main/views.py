from django.shortcuts import render
from django.http import HttpResponse
from .models import Classroom
from .forms import BookingForm


def overview(request):
    return render(request, "main/overview.html")


def classroom_list(request):
    classrooms = Classroom.objects.all()
    return render(request, "main/classroom.html", {"classrooms": classrooms})


def booking(request):
    form = BookingForm()
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
    return render(request, "main/booking.html", {"form": form})
