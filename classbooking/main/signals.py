from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Booking, Classroom


@receiver(post_save, sender=Booking)
def update_classroom_on_booking(sender, instance, created, **kwargs):
    # Mark classroom as unavailable when a booking is created or updated.
    classroom = instance.classroom
    classroom.is_available = False
    classroom.save()


@receiver(post_delete, sender=Booking)
def update_classroom_on_booking_delete(sender, instance, **kwargs):
    # Mark classroom as available again when a booking is deleted.
    classroom = instance.classroom
    classroom.is_available = True
    classroom.save()
