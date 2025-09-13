from django.contrib import admin
from .models import Classroom, Booking


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ("name", "capacity", "is_available", "booked_by")
    list_filter = ("is_available",)
    search_fields = ("name", "booked_by__username")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("classroom", "user", "start_time", "end_time")
    list_filter = ("classroom", "user")
    search_fields = ("classroom__name", "user__username")
    date_hierarchy = "start_time"
