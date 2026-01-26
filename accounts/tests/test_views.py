from django.test import TestCase
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework import status
from accounts.models import CustomUser, Profile
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.serializers import CustomTokenObtainPairSerializer  # corrected import


class AccountsViewsTests(TestCase):
    """
    Comprehensive tests for accounts/views.py.
    Covers all branches: valid/invalid registration, signup,
    admin vs non-admin user creation, profile update/delete permissions,
    token endpoints, duplicate signup, serializer extras, and edge cases.
    """

    def setUp(self):
        self.client = APIClient()
        self.factory = APIRequestFactory()
        self.admin = CustomUser.objects.create_user(
            email="admin@example.com", password="password123", role="admin", username="admin1"
        )
        self.student = CustomUser.objects.create_user(
            email="student@example.com", password="password123", role="student", username="student1"
        )
        self.instructor = CustomUser.objects.create_user(
            email="instructor@example.com", password="password123", role="instructor", username="instructor1"
        )
        # Use the profile automatically created by signals
        self.profile = self.student.profile
        self.profile.bio = "Student bio"
        self.profile.save()

    # --- RegisterView ---
    def test_register_valid(self):
        response = self.client.post("/accounts/register/", {
            "email": "newuser@example.com",
            "password": "password123",
            "role": "student"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_invalid(self):
        response = self.client.post("/accounts/register/", {
            "email": "",  # invalid
            "password": "password123",
            "role": "student"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_email(self):
        response = self.client.post("/accounts/register/", {
            "email": "student@example.com",
            "password": "password123",
            "role": "student"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- SignupView ---
    def test_signup_valid(self):
        response = self.client.post("/accounts/signup/", {
            "email": "signupuser@example.com",
            "password": "password123",
            "role": "student"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("message", response.data)

    def test_signup_invalid(self):
        response = self.client.post("/accounts/signup/", {
            "email": "",  # invalid
            "password": "password123",
            "role": "student"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_duplicate_email(self):
        response = self.client.post("/accounts/signup/", {
            "email": "student@example.com",
            "password": "password123",
            "role": "student"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- CustomUserViewSet ---
    def test_customuser_create_admin_allowed(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post("/accounts/users/", {
            "email": "created@example.com",
            "password": "password123",
            "role": "student"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_customuser_create_non_admin_denied(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post("/accounts/users/", {
            "email": "created@example.com",
            "password": "password123",
            "role": "student"
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_users_admin_allowed(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/accounts/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_users_student_only_self(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get("/accounts/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_users_instructor_only_self(self):
        self.client.force_authenticate(user=self.instructor)
        response = self.client.get("/accounts/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_users_unauthenticated_returns_empty(self):
        response = self.client.get("/accounts/users/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- ProfileViewSet ---
    def test_profile_update_denied_for_other_user(self):
        self.client.force_authenticate(user=self.instructor)
        response = self.client.put(f"/accounts/profiles/{self.profile.id}/", {"bio": "New bio"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_profile_destroy_denied_for_other_user(self):
        self.client.force_authenticate(user=self.instructor)
        response = self.client.delete(f"/accounts/profiles/{self.profile.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_profile_update_success_for_owner(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.put(f"/accounts/profiles/{self.profile.id}/", {"bio": "Updated bio"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["bio"], "Updated bio")

    def test_profile_destroy_success_for_owner(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.delete(f"/accounts/profiles/{self.profile.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_profile_update_allowed_for_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.put(f"/accounts/profiles/{self.profile.id}/", {"bio": "Admin edit"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_profile_destroy_allowed_for_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f"/accounts/profiles/{self.profile.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_profile_create_assigns_user(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post("/accounts/profiles/", {"bio": "Created bio"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["bio"], "Created bio")
        self.assertEqual(response.data["user"], self.student.id)

    def test_profile_access_unauthenticated(self):
        response = self.client.get("/accounts/profiles/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Token Tests ---
    def test_custom_token_contains_extra_fields(self):
        serializer = CustomTokenObtainPairSerializer(data={
            "email": "student@example.com",
            "password": "password123"
        })
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        self.assertIn("id", data)
        self.assertIn("email", data)
        self.assertIn("role", data)

    def test_token_refresh(self):
        refresh = RefreshToken.for_user(self.student)
        response = self.client.post("/accounts/token/refresh/", {"refresh": str(refresh)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_custom_token_serializer_validate_includes_fields(self):
        request = self.factory.post("/accounts/token/", {"email": "student@example.com", "password": "password123"})
        serializer = CustomTokenObtainPairSerializer(data={"email": "student@example.com", "password": "password123"})
        serializer.context["request"] = request
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        self.assertIn("id", data)
        self.assertIn("email", data)
        self.assertIn("role", data)

    def test_custom_token_serializer_invalid_credentials(self):
        request = self.factory.post(
            "/accounts/token/",
            {"email": "student@example.com", "password": "wrongpass"}
        )
        serializer = CustomTokenObtainPairSerializer(
            data={"email": "student@example.com", "password": "wrongpass"}
        )
        serializer.context["request"] = request
        with self.assertRaises(Exception):
            serializer.is_valid(raise_exception=True)
