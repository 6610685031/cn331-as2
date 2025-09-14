from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Classroom, Booking


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "room_number",
        "total_hours",
        "hours_left",
        "capacity",
        "is_available",
        "booked_by",
    )
    list_filter = ("is_available",)
    search_fields = ("name", "room_number", "booked_by__username")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("classroom", "user", "start_time", "end_time")
    list_filter = ("classroom", "user")
    search_fields = ("classroom__name", "classroom__room_number", "user__username")
    date_hierarchy = "start_time"

    def save_model(self, request, obj, form, change):
        # Calculate booking duration
        duration = (obj.end_time - obj.start_time).total_seconds() / 3600.0

        if duration <= 0:
            raise ValidationError(_("End time must be after start time."))

        # Check if exceeds classroom hours left
        if duration > obj.classroom.hours_left:
            raise ValidationError(
                _(f"This classroom only has {obj.classroom.hours_left:.2f} hours left.")
            )

        # Check overlapping bookings
        overlaps = Booking.objects.filter(
            classroom=obj.classroom,
            start_time__lt=obj.end_time,
            end_time__gt=obj.start_time,
        )

        if obj.pk:  # exclude current booking when editing
            overlaps = overlaps.exclude(pk=obj.pk)

        if overlaps.exists():
            raise ValidationError(
                _(f"{obj.classroom.name} is already booked during the selected time.")
            )

        # Save booking normally
        super().save_model(request, obj, form, change)

        # Deduct hours
        obj.classroom.update_hours(duration, obj.user)

    def delete_model(self, request, obj):
        # Restore classroom hours when a booking is removed
        duration = (obj.end_time - obj.start_time).total_seconds() / 3600.0
        classroom = obj.classroom
        classroom.hours_left += duration
        if classroom.hours_left > classroom.total_hours:
            classroom.hours_left = classroom.total_hours
        classroom.is_available = classroom.hours_left > 0
        classroom.save()

        super().delete_model(request, obj)
