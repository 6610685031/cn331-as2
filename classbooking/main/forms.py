from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from .models import Booking, Classroom


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["classroom", "start_time", "end_time"]
        widgets = {
            "start_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    # Add showAll to get whether if we want to make all classroom fields visible or not
    # Defaults at False
    def __init__(
        self,
        *args,
        showAll=False,
        **kwargs,
    ):

        self.showAll = showAll
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Change the placeholder for the classroom dropdown
        self.fields["classroom"].empty_label = "Select a classroom"

        # Only show classrooms that are currently available
        if not showAll:
            self.fields["classroom"].queryset = Classroom.objects.filter(
                is_available=True
            )

        # Current time localized
        now = timezone.localtime()
        now_str = now.strftime("%Y-%m-%dT%H:%M")
        one_hour_later_str = (now + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M")

        # Set frontend restrictions
        self.fields["start_time"].widget.attrs["min"] = now_str
        self.fields["end_time"].widget.attrs["min"] = now_str

        # Set default values if new form
        if not self.is_bound:
            self.initial["start_time"] = now_str
            self.initial["end_time"] = one_hour_later_str

    def clean(self):
        cleaned_data = super().clean()
        classroom = cleaned_data.get("classroom")
        start = cleaned_data.get("start_time")
        end = cleaned_data.get("end_time")
        user = self.user

        # Classroom check
        if not classroom:
            raise forms.ValidationError("Please select a classroom.")

        # Convert naive datetimes (from datetime-local) to aware, in current timezone
        if start and timezone.is_naive(start):
            start = timezone.make_aware(start, timezone.get_current_timezone())
            cleaned_data["start_time"] = start

        if end and timezone.is_naive(end):
            end = timezone.make_aware(end, timezone.get_current_timezone())
            cleaned_data["end_time"] = end

        # Prevent booking in the past
        if start and start < timezone.now():
            raise ValidationError("You cannot book a classroom in the past.")

        # Check time validity
        if start and end and classroom:

            # If end time is before start time throws an error
            duration = (end - start).total_seconds() / 3600.0  # in hours

            if duration <= 0:
                raise forms.ValidationError("End time must be after start time.")

            # Check if booking exceeds remaining hours
            if duration > classroom.hours_left:
                raise forms.ValidationError(
                    f"This classroom only has {classroom.hours_left:.2f} hours left."
                )

            # Check for overlapping bookings
            overlaps = Booking.objects.filter(
                classroom=classroom,
                start_time__lt=end,  # booking starts before this one ends
                end_time__gt=start,  # booking ends after this one starts
            )

            # If editing an existing booking, exclude itself
            if self.instance.pk:
                overlaps = overlaps.exclude(pk=self.instance.pk)

            if overlaps.exists():
                raise forms.ValidationError(
                    f"{classroom.name} is already booked during the selected time."
                )

            # --- ADMIN PERMISSION ---

            # Enforce maximum 1 hour booking for normal users
            # Assuming superusers/staff are allowed longer bookings
            if user and not user.is_staff and (end - start) > timedelta(hours=1):
                raise ValidationError(
                    "You cannot book a classroom for more than 1 hour."
                )

            # Only one booking per classroom per user (unless staff)
            if self.user and not self.user.is_staff:
                existing = Booking.objects.filter(user=self.user, classroom=classroom)
                if self.instance.pk:
                    existing = existing.exclude(pk=self.instance.pk)
                if existing.exists():
                    raise forms.ValidationError(
                        "You have already booked this classroom. Normal users can only book each classroom once."
                    )

            # # OLD: End must be after start
            # if end <= start:
            #     raise ValidationError("End time must be after start time.")

            # # OLD: Prevent overlapping bookings
            # overlapping = Booking.objects.filter(
            #     classroom=classroom, start_time__lt=end, end_time__gt=start
            # )
            # if self.instance.pk:
            #     overlapping = overlapping.exclude(pk=self.instance.pk)

            # if overlapping.exists():
            #     raise ValidationError(
            #         "This classroom is already booked for the selected time."
            #     )

        return cleaned_data
