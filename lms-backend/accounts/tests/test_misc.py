from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import CustomUser, Profile


class AccountsTests(TestCase):
    """
    Test suite for Accounts endpoints.
    Covers registration, JWT login, user listing isolation, and profile management.
    """
    def setUp(self):
        self.client = APIClient()

    def test_user_registration(self):
        response = self.client.post(
            "/api/accounts/register/",
            {
                "username": "newstudent",
                "password": "testpass123",
                "email": "student@example.com",
                "role": "student",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(CustomUser.objects.get().username, "newstudent")

    def test_duplicate_registration_denied(self):
        CustomUser.objects.create_user(
            username="existinguser",
            password="testpass123",
            email="student@example.com",
            role="student",
        )
        response = self.client.post(
            "/api/accounts/register/",
            {
                "username": "newstudent",
                "password": "testpass123",
                "email": "student@example.com",  # duplicate email
                "role": "student",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_jwt_login_with_email(self):
        user = CustomUser.objects.create_user(
            username="loginuser",
            password="testpass123",
            email="login@example.com",
            role="student",
        )
        response = self.client.post(
            "/api/token/",
            {"email": user.email, "password": "testpass123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_invalid_login_denied(self):
        response = self.client.post(
            "/api/token/",
            {"email": "wrong@example.com", "password": "wrongpass"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_listing_requires_authentication(self):
        # Unauthenticated request should fail
        response = self.client.get("/api/accounts/users/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Student should only see themselves
        student = CustomUser.objects.create_user(
            username="listuser",
            password="testpass123",
            email="list@example.com",
            role="student",
        )
        self.client.force_authenticate(user=student)
        response = self.client.get("/api/accounts/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["email"], student.email)

        # Admin should see all users
        admin = CustomUser.objects.create_user(
            username="adminuser",
            password="adminpass123",
            email="admin@example.com",
            role="admin",
        )
        self.client.force_authenticate(user=admin)
        response = self.client.get("/api/accounts/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

    def test_profile_auto_created(self):
        user = CustomUser.objects.create_user(
            username="profileuser",
            password="testpass123",
            email="profile@example.com",
            role="student",
        )
        self.assertTrue(hasattr(user, "profile"))
        self.assertIsInstance(user.profile, Profile)

    def test_profile_update(self):
        user = CustomUser.objects.create_user(
            username="updateuser",
            password="testpass123",
            email="update@example.com",
            role="student",
        )
        self.client.force_authenticate(user=user)
        profile_id = user.profile.id
        response = self.client.patch(
            f"/api/accounts/profile/{profile_id}/",
            {"bio": "Updated bio"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.profile.bio, "Updated bio")

    def test_unauthenticated_profile_update_denied(self):
        user = CustomUser.objects.create_user(
            username="unauthuser",
            password="testpass123",
            email="unauth@example.com",
            role="student",
        )
        profile_id = user.profile.id
        response = self.client.patch(
            f"/api/accounts/profile/{profile_id}/",
            {"bio": "Should not work"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_role_registration_denied(self):
        response = self.client.post(
            "/api/accounts/register/",
            {
                "username": "badrole",
                "password": "testpass123",
                "email": "badrole@example.com",
                "role": "invalidrole",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("role", response.data)

    def test_student_cannot_update_other_profile(self):
        """
        Students should be denied updating another user's profile.
        """
        student1 = CustomUser.objects.create_user(
            username="student1",
            password="testpass123",
            email="student1@example.com",
            role="student",
        )
        student2 = CustomUser.objects.create_user(
            username="student2",
            password="testpass123",
            email="student2@example.com",
            role="student",
        )
        self.client.force_authenticate(user=student1)
        profile_id = student2.profile.id
        response = self.client.patch(
            f"/api/accounts/profile/{profile_id}/",
            {"bio": "Hacked bio"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
