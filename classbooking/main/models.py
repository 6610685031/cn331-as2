from django.db import models
from django.contrib.auth.models import User


class Classroom(models.Model):
    name = models.CharField(max_length=100)
    capacity = models.IntegerField()
    is_available = models.BooleanField(default=True)
    booked_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return self.name


class Booking(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"{self.classroom.name} booked by {self.user.username}"
