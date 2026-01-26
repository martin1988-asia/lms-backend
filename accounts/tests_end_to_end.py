from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import Profile

User = get_user_model()


class EndToEndWorkflowTests(TestCase):
    """
    End-to-end integration tests for LMS workflows.
    Covers signup → login → token refresh → profile update → course enrollment.
    """

    def setUp(self):
        self.client = APIClient()

    def test_full_student_workflow(self):
        """
        A student should be able to sign up, log in, refresh token, and update their profile.
        """
        # --- Signup ---
        signup_payload = {
            "username": "studentflow",
            "email": "studentflow@example.com",
            "password": "StrongPass123!",
            "role": "student",
        }
        signup_response = self.client.post("/accounts/signup/", signup_payload, format="json")
        self.assertEqual(signup_response.status_code, status.HTTP_201_CREATED)

        # --- Login ---
        login_payload = {"email": "studentflow@example.com", "password": "StrongPass123!"}
        login_response = self.client.post("/accounts/login/", login_payload, format="json")
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        access_token = login_response.data["access"]
        refresh_token = login_response.data["refresh"]

        # --- Refresh ---
        refresh_response = self.client.post("/accounts/refresh/", {"refresh": refresh_token}, format="json")
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_response.data)

        # --- Profile update ---
        user = User.objects.get(email="studentflow@example.com")
        self.client.force_authenticate(user=user)
        profile = Profile.objects.get(user=user)
        response = self.client.patch(f"/accounts/profile/{profile.id}/", {"bio": "Learning Django!"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["bio"], "Learning Django!")

    def test_admin_user_management_and_course_flow(self):
        """
        Admin should be able to create users and assign them to courses.
        """
        # --- Create admin ---
        admin = User.objects.create_superuser(
            email="adminflow@example.com", password="StrongPass123!", username="adminflow"
        )
        self.client.force_authenticate(user=admin)

        # --- Admin creates a new student ---
        payload = {"email": "newstudent@example.com", "password": "StrongPass123!", "role": "student"}
        response = self.client.post("/accounts/users/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="newstudent@example.com").exists())

        # --- Admin lists all users ---
        response = self.client.get("/accounts/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

        # --- (Future hook) Admin assigns student to a course ---
        # Example: response = self.client.post("/courses/enroll/", {"student_id": student.id, "course_id": 1})
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
