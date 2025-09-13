import json

from django.shortcuts import render
from django.http import HttpResponse
from django.core.serializers import serialize
from django.utils.timezone import localtime
from django.contrib.auth.decorators import login_required

from .models import Classroom, Booking
from .forms import BookingForm

import json
from django.core.serializers import serialize
from django.utils.timezone import localtime


@login_required
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


@login_required
def classroom_list(request):
    classrooms = Classroom.objects.all()
    return render(request, "main/classroom.html", {"classrooms": classrooms})


@login_required
def booking(request):
    form = BookingForm()
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            form.instance.user = request.user
            form.save()
    return render(request, "main/booking.html", {"form": form})
