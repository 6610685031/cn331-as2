from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import Booking


@receiver(pre_delete, sender=Booking)
def restore_classroom_hours_on_booking_delete(sender, instance, **kwargs):
    """Restore classroom hours when a booking is deleted."""
    if instance.classroom:
        duration = (instance.end_time - instance.start_time).total_seconds() / 3600.0
        instance.classroom.hours_left += duration
        # Make sure it doesn’t exceed total_hours
        if instance.classroom.hours_left > instance.classroom.total_hours:
            instance.classroom.hours_left = instance.classroom.total_hours
        instance.classroom.is_available = instance.classroom.hours_left > 0
        instance.classroom.save()
