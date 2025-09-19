from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Classroom(models.Model):
    # Default the name to "Generic Classroom" to make existing rows populatable
    name = models.CharField(max_length=100)
    # Make the room number unique
    room_number = models.PositiveIntegerField(unique=True)
    # Total available hours for this classroom
    total_hours = models.FloatField()
    # Total capacity of room (It's just there)
    capacity = models.PositiveIntegerField()
    # Remaining hours available
    hours_left = models.FloatField(default=None, editable=False)
    # Class room availability
    is_available = models.BooleanField(default=True)

    def update_hours(self, duration_hours, user):
        # Deduct hours when booked
        if self.hours_left - duration_hours <= 0:
            self.hours_left = 0
            self.is_available = False
        else:
            self.hours_left -= duration_hours
            self.is_available = True
        self.save()

    def reset_hours(self):
        # Reset daily or weekly depending on rules
        self.hours_left = self.total_hours
        self.is_available = True
        self.save()

    def clean(self):
        # If hours_left is null then set it to equal total_hours
        if self.hours_left == None:
            self.hours_left = self.total_hours

        # DEPRECATED: Hours left cannot exceed total hours.
        # if self.hours_left > self.total_hours:
        #     raise ValidationError("Hours left cannot exceed total hours.")

    def save(self, *args, **kwargs):
        # If hours_left is null then set it to equal total_hours
        if self.hours_left == None:
            self.hours_left = self.total_hours

        # This is a failsafe to not letting hours_left go under 0, no matter the circumstances
        if self.hours_left < 0:
            self.hours_left = 0

        # Ensure hours_left is never lower than total_hours
        if self.hours_left > self.total_hours:
            self.hours_left = self.total_hours
        self.is_available = self.hours_left > 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} (ห้อง {self.room_number}) - เหลือ {self.hours_left} ชม."


class Booking(models.Model):
    classroom = models.ForeignKey(
        Classroom, on_delete=models.CASCADE, related_name="bookings"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def clean(self):
        # If classroom is None then raise error
        try:
            classroom = self.classroom
        except Classroom.DoesNotExist:
            # raise ValidationError("Please select a classroom.")
            return

        # Check for overlapping bookings
        overlapping = Booking.objects.filter(
            classroom=self.classroom,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        ).exclude(pk=self.pk)

        if overlapping.exists():
            raise ValidationError("ห้องเรียนนี้ถูกจองตามเวลาที่เลือกไปแล้ว")

    def save(self, *args, **kwargs):
        duration = (
            self.end_time - self.start_time
        ).total_seconds() / 3600.0  # in hours

        super().save(*args, **kwargs)

        # Deduct classroom hours
        self.classroom.update_hours(duration, self.user)

    def __str__(self):
        return f"{self.classroom} จองโดย {self.user} ตั้งแต่ {self.start_time} ถึง {self.end_time}"
