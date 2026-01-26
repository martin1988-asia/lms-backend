from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import Profile

User = get_user_model()


class AccountsIntegrationTests(TestCase):
    """
    Integration tests for the Accounts app.
    Simulates full workflows: signup → login → refresh → profile update → role-based access.
    """

    def setUp(self):
        self.client = APIClient()

    def test_full_signup_login_refresh_flow(self):
        """
        A user should be able to sign up, log in, and refresh their JWT token.
        """
        # --- Signup ---
        signup_payload = {
            "username": "flowuser",
            "email": "flowuser@example.com",
            "password": "securePass123",
            "role": "student",
        }
        signup_response = self.client.post("/accounts/signup/", signup_payload, format="json")
        self.assertEqual(signup_response.status_code, status.HTTP_201_CREATED)

        # --- Login ---
        login_payload = {"email": "flowuser@example.com", "password": "securePass123"}
        login_response = self.client.post("/accounts/login/", login_payload, format="json")
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", login_response.data)
        self.assertIn("refresh", login_response.data)

        # --- Refresh ---
        refresh_token = login_response.data["refresh"]
        refresh_response = self.client.post("/accounts/refresh/", {"refresh": refresh_token}, format="json")
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_response.data)

    def test_profile_update_flow(self):
        """
        A user should be able to update their own profile but not others'.
        """
        # Create two users
        user1 = User.objects.create_user(
            email="owner@example.com", password="securePass123", username="owner"
        )
        user2 = User.objects.create_user(
            email="intruder@example.com", password="securePass123", username="intruder"
        )

        # --- Owner updates their profile ---
        self.client.force_authenticate(user=user1)
        profile = Profile.objects.get(user=user1)
        response = self.client.patch(f"/accounts/profile/{profile.id}/", {"bio": "Updated bio"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["bio"], "Updated bio")

        # --- Intruder tries to update owner's profile ---
        self.client.force_authenticate(user=user2)
        response = self.client.patch(f"/accounts/profile/{profile.id}/", {"bio": "Hacked!"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_user_management_flow(self):
        """
        Admin should be able to list all users and create new ones.
        """
        admin = User.objects.create_superuser(
            email="admin@example.com", password="securePass123", username="admin"
        )
        student = User.objects.create_user(
            email="student@example.com", password="securePass123", username="student"
        )

        # --- Admin lists all users ---
        self.client.force_authenticate(user=admin)
        response = self.client.get("/accounts/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

        # --- Admin creates a new user ---
        payload = {"email": "newuser@example.com", "password": "securePass123", "role": "student"}
        response = self.client.post("/accounts/users/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())
