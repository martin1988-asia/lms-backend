from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import Profile

User = get_user_model()


class AccountsViewsTests(TestCase):
    """
    Test suite for Accounts app views.
    Validates RegisterView, SignupView, CustomUserViewSet, ProfileViewSet, and JWT login.
    """

    def setUp(self):
        self.client = APIClient()
        self.student = User.objects.create_user(
            email="student@example.com",
            password="securePass123",
            username="student",
            role="student"
        )
        self.admin = User.objects.create_superuser(
            email="admin@example.com",
            password="securePass123",
            username="admin"
        )

    def test_register_view_creates_user(self):
        """
        POST /accounts/register/ should create a new user.
        """
        payload = {
            "username": "newregister",
            "email": "newregister@example.com",
            "password": "StrongPass123!",
            "role": "student",
        }
        response = self.client.post("/accounts/register/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="newregister@example.com").exists())

    def test_signup_view_returns_custom_payload(self):
        """
        POST /accounts/signup/ should return custom response payload.
        """
        payload = {
            "username": "signupuser",
            "email": "signupuser@example.com",
            "password": "StrongPass123!",
            "role": "student",
        }
        response = self.client.post("/accounts/signup/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["email"], "signupuser@example.com")

    def test_custom_user_viewset_me_endpoint(self):
        """
        GET /accounts/users/me/ should return the authenticated user's info.
        """
        self.client.force_authenticate(user=self.student)
        response = self.client.get("/accounts/users/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "student@example.com")

    def test_custom_user_viewset_admin_can_list_all_users(self):
        """
        Admin should be able to list all users via /accounts/users/.
        """
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/accounts/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

    def test_profile_viewset_owner_can_update_profile(self):
        """
        A user should be able to update their own profile.
        """
        self.client.force_authenticate(user=self.student)
        profile = Profile.objects.get(user=self.student)
        response = self.client.patch(f"/accounts/profile/{profile.id}/", {"bio": "Updated bio"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["bio"], "Updated bio")

    def test_profile_viewset_non_owner_cannot_update_profile(self):
        """
        Non-owners should not be able to update another user's profile.
        """
        other_profile = Profile.objects.get(user=self.admin)
        self.client.force_authenticate(user=self.student)
        response = self.client.patch(f"/accounts/profile/{other_profile.id}/", {"bio": "Hacked!"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_custom_token_obtain_pair_view_returns_tokens_and_user_info(self):
        """
        POST /accounts/login/ should return JWT tokens and user info.
        """
        payload = {"email": "student@example.com", "password": "securePass123"}
        response = self.client.post("/accounts/login/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["email"], "student@example.com")
        self.assertEqual(response.data["role"], "student")
