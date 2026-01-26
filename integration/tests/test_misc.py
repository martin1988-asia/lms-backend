from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import CustomUser
from courses.models import Course, Enrollment
from assignments.models import Assignment, Submission
from grades.models import Grade


class IntegrationFlowTests(APITestCase):
    """
    End-to-end integration tests across Accounts, Courses, Assignments, Grades,
    Dashboard, and Analytics. Confirms the full workflow works seamlessly.
    """

    def setUp(self):
        # --- Register users ---
        self.student = CustomUser.objects.create_user(
            username="student1", email="student1@example.com",
            password="testpass123", role="student"
        )
        self.instructor = CustomUser.objects.create_user(
            username="instructor1", email="instructor1@example.com",
            password="testpass123", role="instructor"
        )
        self.admin = CustomUser.objects.create_user(
            username="admin1", email="admin1@example.com",
            password="testpass123", role="admin"
        )

        # --- Course created by instructor ---
        self.course = Course.objects.create(
            title="Integration Course", description="Full workflow test", instructor=self.instructor
        )

    def authenticate(self, user):
        """
        Helper method to authenticate a user via JWT using email.
        """
        url = reverse("token_obtain_pair")
        response = self.client.post(
            url, {"email": user.email, "password": "testpass123"}, format="json"
        )
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_full_student_workflow(self):
        """
        Student registers, enrolls, submits assignment, gets graded,
        and sees results in dashboard/analytics.
        """
        # --- Student enrolls in course ---
        self.authenticate(self.student)
        response = self.client.post(reverse("enrollment-list"), {"course": self.course.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # --- Instructor creates assignment ---
        self.authenticate(self.instructor)
        response = self.client.post(reverse("assignment-list"), {
            "title": "Integration Essay",
            "description": "Write an essay",
            "due_date": "2026-02-01",
            "course": self.course.id,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        assignment_id = response.data["id"]

        # --- Student submits assignment ---
        self.authenticate(self.student)
        response = self.client.post(reverse("submission-list"), {
            "assignment": assignment_id,
            "content": "My integration essay content"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        submission_id = response.data["id"]

        # --- Instructor grades submission ---
        self.authenticate(self.instructor)
        response = self.client.post(reverse("grade-list"), {
            "submission": submission_id,
            "score": "95.00",
            "letter": "A",
            "feedback": "Excellent integration test!"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # --- Student sees grade in dashboard ---
        self.authenticate(self.student)
        response = self.client.get(reverse("student-dashboard"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["grades_count"], 1)
        self.assertGreaterEqual(response.data["assignments_count"], 1)

        # --- Student sees analytics ---
        response = self.client.get(reverse("student-analytics"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["grades_count"], 1)
        self.assertGreaterEqual(response.data["assignments_count"], 1)

        # --- Admin sees global stats ---
        self.authenticate(self.admin)
        response = self.client.get(reverse("admin-dashboard"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["total_courses"], 1)
        self.assertGreaterEqual(response.data["total_students"], 1)
        self.assertGreaterEqual(response.data["total_instructors"], 1)
        self.assertGreaterEqual(response.data["total_grades"], 1)

        response = self.client.get(reverse("admin-analytics"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["total_courses"], 1)
        self.assertGreaterEqual(response.data["total_students"], 1)
        self.assertGreaterEqual(response.data["total_instructors"], 1)
        self.assertGreaterEqual(response.data["total_grades"], 1)
