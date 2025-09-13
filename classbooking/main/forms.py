import datetime

from django import forms
from .models import Booking


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
        fields = ["classroom", "start_time", "end_time"]
