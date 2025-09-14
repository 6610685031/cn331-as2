from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import localtime


from .models import Classroom, Booking
from .forms import BookingForm


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
                "color": "#f56954",  # Red for booked
            }
        )

    return render(
        request,
        "main/overview.html",
        {"events": events, "bookings": bookings, "server_timezone": settings.TIME_ZONE},
    )


@login_required
def classroom(request):
    classrooms = Classroom.objects.all()
    return render(request, "main/classroom.html", {"classrooms": classrooms})


@login_required
def booking(request):
    if request.user.is_staff:
        # Admins see every booking
        user_bookings = Booking.objects.all()
    else:
        # Normal users see only their own
        user_bookings = Booking.objects.filter(user=request.user).order_by("start_time")

    if request.method == "POST":
        form = BookingForm(request.POST, user=request.user)

        # Debug messages for testing
        # messages.info(request, list(list(request.POST.items())))
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user  # Assign logged-in user
            booking.save()  # Signals update classroom availability automatically
            messages.success(request, "Classroom booked successfully!")
            return redirect("overview")
    else:
        form = BookingForm(user=request.user)

    return render(
        request, "main/booking.html", {"form": form, "bookings": user_bookings}
    )


@login_required
def booking_edit(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)

    # Only allow owner or staff
    if booking.user != request.user and not request.user.is_staff:
        raise PermissionDenied("You cannot edit this booking.")

    if request.method == "POST":

        # Workaround form limitation by manually getting id, classroom_id
        appended_post = request.POST.copy()
        appended_post["id"] = pk
        appended_post["classroom"] = Booking.objects.get(pk=pk).classroom_id

        # Then set the request to BookingForm that has showAll=true
        form = BookingForm(
            appended_post, instance=booking, showAll=True, user=request.user
        )

        if form.is_valid():
            # I don't even fucking know what this does
            classroom = booking.classroom
            duration = (booking.end_time - booking.start_time).total_seconds() / 3600.0

            # Restore classroom hours
            classroom.hours_left += duration
            if classroom.hours_left > classroom.total_hours:
                classroom.hours_left = classroom.total_hours
            classroom.is_available = classroom.hours_left > 0
            classroom.save()

            # Save the form
            form.save()

            messages.success(request, "Booking updated successfully!")
            return redirect("booking")
    else:
        form = BookingForm(instance=booking, user=request.user)

    current_booking = Booking.objects.get(pk=pk)
    return render(
        request,
        "main/booking.html",
        {
            "form": form,
            # Actually we don't need it but leave it in anyways
            "bookings": booking,
            "edit_mode": "on",
            "current_booking_name": current_booking.classroom,
        },
    )


@login_required
def booking_cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)

    # Permission checker
    if booking.user != request.user and not request.user.is_staff:
        raise PermissionDenied("You cannot cancel this booking.")

    # Calculate booked hours
    classroom = booking.classroom
    duration = (booking.end_time - booking.start_time).total_seconds() / 3600.0

    # Restore classroom hours
    classroom.hours_left += duration
    if classroom.hours_left > classroom.total_hours:
        classroom.hours_left = classroom.total_hours
    classroom.is_available = classroom.hours_left > 0
    classroom.save()

    # Delete booking
    booking.delete()

    messages.success(request, f"Your booking for {classroom.name} has been canceled.")
    return redirect("booking")  # Redirect back to your booking page
