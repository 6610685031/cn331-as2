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
        user = self.instance.user

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

        # End must be after start
        if start and end:
            if end <= start:
                raise ValidationError("End time must be after start time.")

            # Enforce maximum 1 hour booking for normal users
            # Assuming superusers/staff are allowed longer bookings
            if user and not user.is_staff and (end - start) > timedelta(hours=1):
                raise ValidationError(
                    "You cannot book a classroom for more than 1 hour."
                )

        # Prevent overlapping bookings
        if start and end and classroom:
            overlapping = Booking.objects.filter(
                classroom=classroom, start_time__lt=end, end_time__gt=start
            )
            if self.instance.pk:
                overlapping = overlapping.exclude(pk=self.instance.pk)

            if overlapping.exists():
                raise ValidationError(
                    "This classroom is already booked for the selected time."
                )

        return cleaned_data
