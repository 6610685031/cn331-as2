from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from .models import Booking


@receiver(pre_delete, sender=Booking)
def restore_classroom_hours_on_booking_delete(sender, instance, **kwargs):
    """Restore classroom hours when a booking is deleted."""
    if instance.classroom:
        duration = (instance.end_time - instance.start_time).total_seconds() / 3600.0
        instance.classroom.hours_left += duration
        # Ensure it never exceeds the total hours
        if instance.classroom.hours_left > instance.classroom.total_hours:
            instance.classroom.hours_left = instance.classroom.total_hours
        instance.classroom.is_available = instance.classroom.hours_left > 0
        instance.classroom.save()


@receiver(pre_save, sender=Booking)
def adjust_classroom_hours_on_booking_edit(sender, instance, **kwargs):
    """Adjust classroom hours if a booking is edited."""
    if not instance.pk:
        # New booking — handled by your existing booking creation logic
        return

    try:
        old_booking = Booking.objects.get(pk=instance.pk)
    except Booking.DoesNotExist:
        return

    old_duration = (
        old_booking.end_time - old_booking.start_time
    ).total_seconds() / 3600.0
    new_duration = (instance.end_time - instance.start_time).total_seconds() / 3600.0

    # If the classroom changes, restore old and deduct from new
    if old_booking.classroom != instance.classroom:
        # Restore hours to the old classroom
        if old_booking.classroom:
            old_booking.classroom.hours_left += old_duration
            if old_booking.classroom.hours_left > old_booking.classroom.total_hours:
                old_booking.classroom.hours_left = old_booking.classroom.total_hours
            old_booking.classroom.is_available = old_booking.classroom.hours_left > 0
            old_booking.classroom.save()

        # Deduct from the new classroom
        if instance.classroom:
            instance.classroom.hours_left -= new_duration
            if instance.classroom.hours_left < 0:
                instance.classroom.hours_left = 0
            instance.classroom.is_available = instance.classroom.hours_left > 0
            instance.classroom.save()
    else:
        # Same classroom — adjust only the difference in duration
        delta = new_duration - old_duration
        if delta != 0 and instance.classroom:
            instance.classroom.hours_left -= delta
            if instance.classroom.hours_left < 0:
                instance.classroom.hours_left = 0
            if instance.classroom.hours_left > instance.classroom.total_hours:
                instance.classroom.hours_left = instance.classroom.total_hours
            instance.classroom.is_available = instance.classroom.hours_left > 0
            instance.classroom.save()
