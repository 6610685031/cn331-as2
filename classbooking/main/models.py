from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Classroom(models.Model):
    # Default the name to "Generic Classroom" to make existing rows populatable
    name = models.CharField(max_length=100, default="Generic Classroom", null=True)
    # Make the room number unique
    room_number = models.PositiveIntegerField(unique=True)
    capacity = models.PositiveIntegerField()
    is_available = models.BooleanField(default=True)
    booked_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return f"{self.name} (Room No. {self.room_number})"


class Booking(models.Model):
    classroom = models.ForeignKey(
        Classroom, on_delete=models.CASCADE, related_name="bookings"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def clean(self):
        # Check for overlapping bookings
        overlapping = Booking.objects.filter(
            classroom=self.classroom,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        ).exclude(pk=self.pk)

        if overlapping.exists():
            raise ValidationError(
                "This classroom is already booked for the selected time."
            )

    def __str__(self):
        return f"{self.classroom.name} (reserved by {self.user.username})"
