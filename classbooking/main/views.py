from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import localtime


from .models import Classroom, Booking
from .forms import ClassroomForm, BookingForm


@login_required
def overview(request):
    bookings = Booking.objects.select_related("classroom", "user")
    events = []

    for b in bookings:
        events.append(
            {
                "title": f"{b.classroom.name} ({b.classroom.room_number}) - {b.user.username}",
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
            return redirect("booking")
    else:
        form = BookingForm(user=request.user)

    return render(
        request, "main/booking.html", {"form": form, "bookings": user_bookings}
    )


@login_required
def booking_edit(request, pk):
    # If admin then allow for all bookings to be edited
    if request.user.is_staff:
        booking = get_object_or_404(Booking, pk=pk)
    else:
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
            # Get the correct classroom and unedited booking object
            old_booking = get_object_or_404(Booking, pk=pk)
            classroom = booking.classroom
            duration = (
                old_booking.end_time - old_booking.start_time
            ).total_seconds() / 3600.0

            # Restore classroom hours
            classroom.hours_left += duration
            if classroom.hours_left > classroom.total_hours:
                classroom.hours_left = classroom.total_hours
            classroom.is_available = classroom.hours_left > 0

            # Save the classroom object
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
    # If admin then allow for all bookings to be canceled
    if request.user.is_staff:
        booking = get_object_or_404(Booking, pk=pk)
    else:
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


@login_required
def classroom(request):
    classrooms = Classroom.objects.all()
    return render(request, "main/classroom.html", {"classrooms": classrooms})


@staff_member_required
def classroom_add(request):
    if request.method == "POST":
        form = ClassroomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("classroom")
    else:
        form = ClassroomForm()
    return render(
        request, "main/classroom/edit.html", {"form": form, "title": "Add Classroom"}
    )


@staff_member_required
def classroom_edit(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk)
    if request.method == "POST":
        form = ClassroomForm(request.POST, instance=classroom)

        if form.is_valid():
            # get the unchanged classroom data
            old_classroom = get_object_or_404(Classroom, pk=pk)

            # create variable named total_hours_diff to check changed value (total_hours_diff can only go positive)
            total_hours_diff = classroom.total_hours - old_classroom.total_hours
            total_hours_diff = total_hours_diff if not (total_hours_diff < 0) else 0

            # get already booked hours from old classroom (before form changes)
            hours_left_diff = old_classroom.hours_left - old_classroom.total_hours
            # if total hours diff is more than 0 don't change hours left
            hours_left_diff = hours_left_diff if not (total_hours_diff > 0) else 0

            # DEBUG: messages for total_hours_diff and hours_left_diff
            messages.success(
                request,
                f"total_hours_diff = {total_hours_diff}, hours_left_diff = {hours_left_diff}",
            )

            # commit the form
            form.save()

            # if hours_left is less than 0 then something is totally wrong with the admin
            # since you can't directly set hours_left in the first place, it must be the admin setting it lower than 0
            if (classroom.hours_left + total_hours_diff + hours_left_diff) < 0:
                # raise an error
                form.add_error(
                    "total_hours",
                    forms.ValidationError(
                        "Total hours must not be lower than the total hours booked from all bookings."
                    ),
                )

                # reset the classroom value
                classroom.total_hours = old_classroom.total_hours
                classroom.hours_left = old_classroom.hours_left

                # then save the classroom object
                classroom.save()
            else:

                # if total_hours increase then increment hours_left by the same amount
                classroom.hours_left = (
                    classroom.hours_left + total_hours_diff + hours_left_diff
                )
                # then save the classroom object
                classroom.save()

                return redirect("classroom")
    else:
        form = ClassroomForm(instance=classroom)
    return render(
        request, "main/classroom/edit.html", {"form": form, "title": "Edit Classroom"}
    )


@staff_member_required
def classroom_remove(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk)
    if request.method == "POST":
        classroom.delete()
        return redirect("classroom")
    return render(request, "main/classroom/remove.html", {"classroom": classroom})
