from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Classroom(models.Model):
    # Default the name to "Generic Classroom" to make existing rows populatable
    name = models.CharField(max_length=100, default="Generic Classroom")
    # Make the room number unique
    room_number = models.PositiveIntegerField(unique=True)
    # Total available hours for this classroom
    total_hours = models.PositiveIntegerField(default=8)
    # Total capacity of room (It's just there)
    capacity = models.PositiveIntegerField()
    # Remaining hours available
    hours_left = models.FloatField(default=8.0)
    # Class room availability
    is_available = models.BooleanField(default=True)
    # Who booked the classroom
    booked_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    def update_hours(self, duration_hours, user):
        # Deduct hours when booked
        if self.hours_left - duration_hours <= 0:
            self.hours_left = 0
            self.is_available = False
        else:
            self.hours_left -= duration_hours
            self.is_available = True
        self.booked_by = user
        self.save()

    def reset_hours(self):
        # Reset daily or weekly depending on rules
        self.hours_left = self.total_hours
        self.is_available = True
        self.booked_by = None
        self.save()

    def __str__(self):
        return f"{self.name} (Room No. {self.room_number}) - {self.hours_left}h left"


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

    def save(self, *args, **kwargs):
        duration = (
            self.end_time - self.start_time
        ).total_seconds() / 3600.0  # in hours

        super().save(*args, **kwargs)

        # Deduct classroom hours
        self.classroom.update_hours(duration, self.user)

    def __str__(self):
        return f"{self.classroom} booked by {self.user} from {self.start_time} to {self.end_time}"
