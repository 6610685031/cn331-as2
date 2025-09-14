from django.contrib import admin
from .models import Classroom, Booking


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ("name", "room_number", "capacity", "is_available", "booked_by")
    list_filter = ("is_available",)
    search_fields = ("name", "room_number", "booked_by__username")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("classroom", "user", "start_time", "end_time")
    list_filter = ("classroom", "user")
    search_fields = ("classroom__name", "classroom__room_number", "user__username")
    date_hierarchy = "start_time"

    def save_model(self, request, obj, form, change):
        # Save the booking
        super().save_model(request, obj, form, change)

        # Update classroom availability
        obj.classroom.is_available = False
        obj.classroom.booked_by = obj.user
        obj.classroom.save()

    def delete_model(self, request, obj):
        # Reset classroom availability before deleting booking
        classroom = obj.classroom
        super().delete_model(request, obj)

        # Update classroom availability
        classroom.is_available = True
        classroom.booked_by = None
        classroom.save()
