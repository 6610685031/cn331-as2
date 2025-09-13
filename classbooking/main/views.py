import json

from django.shortcuts import render
from django.http import HttpResponse
from django.core.serializers import serialize
from django.utils.timezone import localtime

from .models import Classroom, Booking
from .forms import BookingForm


def overview(request):
    bookings = Booking.objects.select_related("classroom", "user")
    events = []

    for b in bookings:
        events.append(
            {
                "title": f"{b.classroom.name} - {b.user.username}",
                "start": localtime(b.start_time).isoformat(),
                "end": localtime(b.end_time).isoformat(),
            }
        )

    return render(
        request,
        "main/overview.html",
        {"events": json.dumps(events), "bookings": bookings},
    )


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
