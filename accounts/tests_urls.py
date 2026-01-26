from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class AccountsURLsTests(TestCase):
    """
    Test suite for Accounts app URLs.
    Ensures endpoints are correctly wired and functional.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="urltest@example.com",
            password="securePass123",
            username="urltester"
        )

    def test_signup_endpoint(self):
        """
        /accounts/signup/ should create a new user.
        """
        payload = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securePass123",
            "role": "student",
        }
        response = self.client.post("/accounts/signup/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())

    def test_login_endpoint_returns_tokens(self):
        """
        /accounts/login/ should return JWT tokens.
        """
        payload = {"email": "urltest@example.com", "password": "securePass123"}
        response = self.client.post("/accounts/login/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_refresh_endpoint_returns_new_access_token(self):
        """
        /accounts/refresh/ should return a new access token.
        """
        payload = {"email": "urltest@example.com", "password": "securePass123"}
        login_response = self.client.post("/accounts/login/", payload, format="json")
        refresh_token = login_response.data["refresh"]

        response = self.client.post("/accounts/refresh/", {"refresh": refresh_token}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_profile_me_endpoint(self):
        """
        /accounts/profile/me/ should return the authenticated user's profile.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/accounts/profile/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "urltest@example.com")

    def test_users_list_endpoint_admin_only(self):
        """
        /accounts/users/ should only be accessible to admins.
        """
        # Normal user should only see themselves
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/accounts/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["email"], "urltest@example.com")

        # Admin should see all users
        admin = User.objects.create_superuser(
            email="admin@example.com",
            password="securePass123",
            username="adminuser"
        )
        self.client.force_authenticate(user=admin)
        response = self.client.get("/accounts/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)
