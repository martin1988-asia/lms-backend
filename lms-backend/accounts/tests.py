from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import Profile

User = get_user_model()


class AccountsTests(TestCase):
    """
    Test suite for the Accounts app.
    Covers user creation, profile auto-creation, and JWT authentication.
    """

    def setUp(self):
        self.client = APIClient()

    def test_user_registration_creates_profile(self):
        """
        Registering a new user should automatically create a Profile via signals.
        """
        user = User.objects.create_user(
            email="testuser@example.com",
            password="securePass123",
            username="testuser"
        )
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_register_api_creates_user_and_profile(self):
        """
        POST /accounts/signup/ should create a user and profile.
        """
        payload = {
            "username": "apiuser",
            "email": "apiuser@example.com",
            "password": "securePass123",
            "role": "student",
        }
        response = self.client.post("/accounts/signup/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="apiuser@example.com").exists())
        user = User.objects.get(email="apiuser@example.com")
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_jwt_login_returns_token_and_user_info(self):
        """
        POST /accounts/login/ should return JWT tokens and user info.
        """
        user = User.objects.create_user(
            email="jwtuser@example.com",
            password="securePass123",
            username="jwtuser"
        )
        payload = {"email": "jwtuser@example.com", "password": "securePass123"}
        response = self.client.post("/accounts/login/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["email"], "jwtuser@example.com")
        self.assertEqual(response.data["role"], "student")

    def test_profile_update_restricted_for_non_owner(self):
        """
        Non-admin users should not be able to update another user's profile.
        """
        user1 = User.objects.create_user(
            email="owner@example.com",
            password="securePass123",
            username="owner"
        )
        user2 = User.objects.create_user(
            email="intruder@example.com",
            password="securePass123",
            username="intruder"
        )
        self.client.force_authenticate(user=user2)
        profile = Profile.objects.get(user=user1)
        response = self.client.patch(f"/accounts/profile/{profile.id}/", {"bio": "Hacked!"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
