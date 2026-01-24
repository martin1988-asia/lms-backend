from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import CustomUser, Profile


class AccountsTests(TestCase):
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

    def test_jwt_login(self):
        user = CustomUser.objects.create_user(
            username="loginuser",
            password="testpass123",
            email="login@example.com",
            role="student",
        )
        response = self.client.post(
            "/api/token/",
            {"username": "loginuser", "password": "testpass123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_user_listing_requires_authentication(self):
        response = self.client.get("/api/accounts/users/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        user = CustomUser.objects.create_user(
            username="listuser",
            password="testpass123",
            email="list@example.com",
            role="student",
        )
        self.client.force_authenticate(user=user)
        response = self.client.get("/api/accounts/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

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
        response = self.client.patch(
            "/api/accounts/profile/1/",
            {"bio": "Updated bio"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.profile.bio, "Updated bio")
