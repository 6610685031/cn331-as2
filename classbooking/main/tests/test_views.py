from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from main.models import Classroom, Booking


class ViewTests(TestCase):
    def setUp(self):
        # Create a normal user and an admin
        self.user = User.objects.create_user(username="user", password="pass1234")
        self.admin = User.objects.create_superuser(
            username="admin", password="admin1234"
        )

        # Create a classroom
        self.classroom = Classroom.objects.create(
            name="Room A",
            room_number=101,
            total_hours=10,
            hours_left=10,
            capacity=40,
            is_available=True,
        )

        # Create a booking
        self.booking = Booking.objects.create(
            classroom=self.classroom,
            user=self.user,
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=1),
        )

    # -------------------------------
    # Overview Page
    # -------------------------------
    def test_overview_page_loads(self):
        """Overview page should render for authenticated users."""
        self.client.login(username="user", password="pass1234")
        response = self.client.get(reverse("overview"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "main/overview.html")

    # -------------------------------
    # Classroom Page
    # -------------------------------
    def test_classroom_page_renders_classrooms(self):
        """Classrooms page should list all classrooms."""
        self.client.login(username="user", password="pass1234")
        response = self.client.get(reverse("classroom"))
        self.assertContains(response, "Room A")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "main/classroom.html")

    # -------------------------------
    # Booking Page
    # -------------------------------
    def test_booking_page_loads_and_shows_user_bookings(self):
        """Booking page should show the current user's bookings."""
        self.client.login(username="user", password="pass1234")
        response = self.client.get(reverse("booking"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Room A")
        self.assertTemplateUsed(response, "main/booking.html")

    def test_admin_booking_page_shows_all_bookings(self):
        """Admin booking page should show all users' bookings."""
        self.client.login(username="admin", password="admin1234")
        response = self.client.get(reverse("booking"))
        self.assertContains(response, "Room A")
        self.assertContains(response, "user")  # booked by user
        self.assertEqual(response.status_code, 200)

    # -------------------------------
    # Delete Account Page
    # -------------------------------
    def test_delete_account_page_renders_for_user(self):
        """Delete account page should load for normal user."""
        self.client.login(username="user", password="pass1234")
        response = self.client.get(reverse("auth_deletion"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Account Deletion")

    def test_delete_account_blocks_admin(self):
        """Admins cannot delete their own account."""
        self.client.login(username="admin", password="admin1234")
        response = self.client.post(reverse("auth_deletion"))

        self.assertRedirects(response, reverse("overview"))

        # messages = list(response.wsgi_request._messages)
        # self.assertTrue(any("cannot be deleted" in str(m) for m in messages))

    def test_delete_account_removes_user_and_bookings(self):
        """Deleting a user should cascade-delete their bookings."""
        self.client.login(username="user", password="pass1234")
        response = self.client.post(reverse("auth_deletion"))
        self.assertRedirects(response, reverse("auth_login"))

        # Ensure user and booking are deleted
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username="user")
        self.assertEqual(Booking.objects.count(), 0)
