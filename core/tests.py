
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from .models import DonorProfile, VolunteerProfile


class BloodBridgeTests(TestCase):

    def setUp(self):
        self.donor_user = User.objects.create_user(
            username="arun",
            password="TestPass123!"
        )

        self.donor = DonorProfile.objects.create(
            user=self.donor_user,
            full_name="Arun Kumar",
            phone="9876543210",
            blood_group="O+",
            city="Chennai",
            is_available=True
        )

    def test_home_page_loads(self):
        response = self.client.get(reverse("search_donors"))
        self.assertEqual(response.status_code, 200)

    def test_donor_appears_in_search(self):
        response = self.client.get(reverse("search_donors"))
        self.assertContains(response, "Arun Kumar")
        self.assertContains(response, "9876543210")

    def test_search_by_blood_group(self):
        response = self.client.get(
            reverse("search_donors"),
            {"blood_group": "O+"}
        )
        self.assertContains(response, "Arun Kumar")

    def test_search_by_city(self):
        response = self.client.get(
            reverse("search_donors"),
            {"city": "Chennai"}
        )
        self.assertContains(response, "Arun Kumar")

    def test_unavailable_donor_not_shown(self):
        self.donor.is_available = False
        self.donor.save()

        response = self.client.get(reverse("search_donors"))
        self.assertNotContains(response, "Arun Kumar")

    def test_donor_login_success(self):
        response = self.client.post(
            reverse("donor_login"),
            {
                "username": "arun",
                "password": "TestPass123!"
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            User.objects.get(username="arun").is_authenticated
            if hasattr(User.objects.get(username="arun"), "is_authenticated")
            else True
        )
        self.assertIn("_auth_user_id", self.client.session)

    def test_donor_login_invalid_password(self):
        response = self.client.post(
            reverse("donor_login"),
            {
                "username": "arun",
                "password": "WrongPassword"
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_edit_profile_updates_database(self):
        self.client.force_login(self.donor_user)

        response = self.client.post(
            reverse("edit_profile"),
            {
                "full_name": "Arun Updated",
                "phone": "9123456789",
                "blood_group": "A+",
                "city": "Madurai"
            }
        )

        self.donor.refresh_from_db()

        self.assertEqual(self.donor.full_name, "Arun Updated")
        self.assertEqual(self.donor.phone, "9123456789")
        self.assertEqual(self.donor.blood_group, "A+")
        self.assertEqual(self.donor.city, "Madurai")
        self.assertEqual(response.status_code, 302)

    def test_availability_can_be_toggled(self):
        self.client.force_login(self.donor_user)

        response = self.client.post(
            reverse("update_availability")
        )

        self.donor.refresh_from_db()

        self.assertFalse(self.donor.is_available)
        self.assertEqual(response.status_code, 302)

    def test_volunteer_registration_page_loads(self):
        response = self.client.get(
            reverse("register_volunteer")
        )
        self.assertEqual(response.status_code, 200)

    def test_volunteer_registration_creates_account(self):
        response = self.client.post(
            reverse("register_volunteer"),
            {
                "full_name": "Priya",
                "username": "priya_volunteer",
                "password": "VolunteerPass123!",
                "phone": "9876501234",
                "city": "Chennai"
            }
        )

        self.assertTrue(
            User.objects.filter(username="priya_volunteer").exists()
        )
        self.assertTrue(
            VolunteerProfile.objects.filter(
                user__username="priya_volunteer"
            ).exists()
        )
        self.assertEqual(response.status_code, 302)

    def test_volunteer_login_redirects_to_dashboard(self):
        volunteer_user = User.objects.create_user(
            username="volunteer1",
            password="VolunteerPass123!"
        )

        VolunteerProfile.objects.create(
            user=volunteer_user,
            full_name="Priya",
            phone="9876501234",
            city="Chennai"
        )

        response = self.client.post(
            reverse("donor_login"),
            {
                "username": "volunteer1",
                "password": "VolunteerPass123!"
            }
        )

        self.assertRedirects(
            response,
            reverse("volunteer_dashboard"),
            fetch_redirect_response=False
        )
