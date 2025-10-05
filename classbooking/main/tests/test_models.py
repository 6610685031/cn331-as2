from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from main.models import Classroom, Booking


class BookingSystemTests(TestCase):
    def setUp(self):
        # Create normal user and admin
        self.user = User.objects.create_user(username="user1", password="pass1234")
        self.admin = User.objects.create_superuser(
            username="admin", password="admin1234"
        )

        # Create classroom
        self.classroom = Classroom.objects.create(
            name="Room A",
            room_number=101,
            total_hours=10,
            hours_left=10,
            capacity=40,
            is_available=True,
        )

    def test_booking_creation_deducts_hours(self):
        """Booking reduces classroom hours_left correctly."""

        # login as an admin
        self.client.login(username="admin", password="admin1234")

        start = timezone.now()
        end = start + timedelta(hours=2)

        booking = Booking.objects.create(
            classroom=self.classroom, user=self.user, start_time=start, end_time=end
        )

        self.classroom.refresh_from_db()
        self.assertAlmostEqual(self.classroom.hours_left, 8)
        self.assertFalse(self.classroom.is_available == False)

    def test_booking_delete_restores_hours(self):
        """Deleting a booking restores classroom hours."""

        # login as an admin
        self.client.login(username="admin", password="admin1234")

        start = timezone.now()
        end = start + timedelta(hours=3)
        booking = Booking.objects.create(
            classroom=self.classroom, user=self.user, start_time=start, end_time=end
        )
        self.classroom.refresh_from_db()
        self.assertEqual(self.classroom.hours_left, 7)

        # Delete booking
        booking.delete()
        self.classroom.refresh_from_db()
        self.assertEqual(self.classroom.hours_left, 10)

    def test_user_cannot_book_more_than_one_hour(self):
        """Normal user cannot book more than 1 hour."""

        # login as normal user
        self.client.login(username="user1", password="pass1234")

        start = timezone.now()
        end = start + timedelta(hours=2)
        with self.assertRaises(Exception):
            booking = Booking.objects.create(
                classroom=self.classroom, user=self.user, start_time=start, end_time=end
            )
            booking.clean()
            booking.save()

    def test_admin_can_book_longer_than_one_hour(self):
        """Admin/superuser can bypass 1-hour restriction."""

        # login as an admin
        self.client.login(username="admin", password="admin1234")

        start = timezone.now()
        end = start + timedelta(hours=3)
        booking = Booking.objects.create(
            classroom=self.classroom, user=self.admin, start_time=start, end_time=end
        )
        self.classroom.refresh_from_db()
        self.assertEqual(self.classroom.hours_left, 7)

    def test_user_can_only_book_classroom_once(self):
        """Normal user cannot book the same classroom twice."""

        # login as normal user
        self.client.login(username="user1", password="pass1234")

        start = timezone.now()
        end = start + timedelta(hours=1)
        Booking.objects.create(
            classroom=self.classroom, user=self.user, start_time=start, end_time=end
        )
        with self.assertRaises(Exception):
            booking = Booking.objects.create(
                classroom=self.classroom,
                user=self.user,
                start_time=start + timedelta(days=1),
                end_time=end + timedelta(days=1),
            )
            booking.clean()
            booking.save()

    def test_delete_account_removes_bookings_and_restores_hours(self):
        """Deleting user should cascade delete bookings and restore classroom hours."""
        start = timezone.now()
        end = start + timedelta(hours=2)
        booking = Booking.objects.create(
            classroom=self.classroom, user=self.user, start_time=start, end_time=end
        )
        self.classroom.refresh_from_db()
        self.assertEqual(self.classroom.hours_left, 8)

        # Delete user (should cascade delete bookings)
        self.user.delete()
        self.classroom.refresh_from_db()
        self.assertEqual(self.classroom.hours_left, 10)
