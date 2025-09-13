import datetime

from django import forms
from django.core.exceptions import ValidationError

from .models import Booking, Classroom


# DateTime workaround for Django
# https://stackoverflow.com/questions/50214773/type-datetime-local-in-django-form
class DateTimeLocalInput(forms.DateTimeInput):
    input_type = "datetime-local"


class DateTimeLocalField(forms.DateTimeField):
    # Set DATETIME_INPUT_FORMATS here because, if USE_L10N
    # is True, the locale-dictated format will be applied
    # instead of settings.DATETIME_INPUT_FORMATS.
    # See also:
    # https://developer.mozilla.org/en-US/docs/Web/HTML/Date_and_time_formats

    input_formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M",
    ]
    widget = DateTimeLocalInput(format="%Y-%m-%dT%H:%M")


class BookingForm(forms.ModelForm):
    start_time = DateTimeLocalField()
    end_time = DateTimeLocalField()

    class Meta:
        model = Booking
        fields = ["classroom", "start_time", "end_time"]  # user assigned in view

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show classrooms that are currently available
        self.fields["classroom"].queryset = Classroom.objects.filter(is_available=True)

    def clean(self):
        cleaned_data = super().clean()
        classroom = cleaned_data.get("classroom")
        start = cleaned_data.get("start_time")
        end = cleaned_data.get("end_time")

        if start and end and classroom:
            # Check for overlapping bookings
            overlapping = Booking.objects.filter(
                classroom=classroom, start_time__lt=end, end_time__gt=start
            )
            if self.instance.pk:
                overlapping = overlapping.exclude(pk=self.instance.pk)

            if overlapping.exists():
                raise ValidationError(
                    "This classroom is already booked for the selected time."
                )
