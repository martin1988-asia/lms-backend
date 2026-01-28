from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import Profile

User = get_user_model()


class AccountsPermissionsTests(TestCase):
    """
    Test suite for role-based permissions in the Accounts app.
    Ensures that students, instructors, and admins have correct access.
    """

    def setUp(self):
        self.client = APIClient()
        self.student = User.objects.create_user(
            email="student@example.com",
            password="securePass123",
            username="student",
            role="student"
        )
        self.instructor = User.objects.create_user(
            email="instructor@example.com",
            password="securePass123",
            username="instructor",
            role="instructor"
        )
        self.admin = User.objects.create_superuser(
            email="admin@example.com",
            password="securePass123",
            username="admin"
        )

    def test_student_cannot_create_users(self):
        """
        Students should not be able to create new users via /users/.
        """
        self.client.force_authenticate(user=self.student)
        payload = {"email": "new@example.com", "password": "securePass123", "role": "student"}
        response = self.client.post("/accounts/users/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_instructor_cannot_create_users(self):
        """
        Instructors should not be able to create new users via /users/.
        """
        self.client.force_authenticate(user=self.instructor)
        payload = {"email": "new@example.com", "password": "securePass123", "role": "student"}
        response = self.client.post("/accounts/users/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_users(self):
        """
        Admins should be able to create new users via /users/.
        """
        self.client.force_authenticate(user=self.admin)
        payload = {"email": "newadmin@example.com", "password": "securePass123", "role": "student"}
        response = self.client.post("/accounts/users/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="newadmin@example.com").exists())

    def test_student_can_only_access_own_profile(self):
        """
        Students should only be able to access their own profile.
        """
        other_profile = Profile.objects.get(user=self.instructor)
        self.client.force_authenticate(user=self.student)
        response = self.client.get(f"/accounts/profile/{other_profile.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_access_all_profiles(self):
        """
        Admins should be able to access any profile.
        """
        other_profile = Profile.objects.get(user=self.student)
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(f"/accounts/profile/{other_profile.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
