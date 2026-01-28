from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import CustomUser
from courses.models import Course
from assignments.models import Assignment, Submission


class AssignmentTests(APITestCase):
    """
    Test suite for AssignmentViewSet.
    Covers instructor assignment creation, listing, and denial cases.
    """
    def setUp(self):
        # --- Instructor user ---
        self.instructor = CustomUser.objects.create_user(
            username="instructor1",
            email="instructor1@example.com",
            password="testpass123",
            role="instructor",
        )
        self.course = Course.objects.create(
            title="Biology 101",
            description="Intro to biology",
            instructor=self.instructor,
        )
        # Authenticate as instructor using email
        url = reverse("token_obtain_pair")
        response = self.client.post(
            url, {"email": self.instructor.email, "password": "testpass123"}, format="json"
        )
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_create_assignment(self):
        url = reverse("assignment-list")
        data = {
            "title": "Lab Report",
            "description": "Write a lab report",
            "due_date": "2026-01-31",
            "course": self.course.id,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Assignment.objects.count(), 1)

    def test_list_assignments(self):
        Assignment.objects.create(
            title="Essay", description="Write an essay", due_date="2026-02-01", course=self.course
        )
        url = reverse("assignment-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_non_instructor_cannot_create_assignment(self):
        student = CustomUser.objects.create_user(
            username="student1", email="student1@example.com",
            password="testpass123", role="student"
        )
        url = reverse("token_obtain_pair")
        response = self.client.post(
            url, {"email": student.email, "password": "testpass123"}, format="json"
        )
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        url = reverse("assignment-list")
        data = {"title": "Invalid", "description": "Should fail", "due_date": "2026-03-01", "course": self.course.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_assignment_missing_title(self):
        """
        Assignment creation should fail if required fields are missing.
        """
        url = reverse("assignment-list")
        data = {"description": "No title", "due_date": "2026-04-01", "course": self.course.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)


class SubmissionTests(APITestCase):
    """
    Test suite for SubmissionViewSet.
    Covers student submission creation, listing, and denial cases.
    """
    def setUp(self):
        # --- Users ---
        self.student = CustomUser.objects.create_user(
            username="student1",
            email="student1@example.com",
            password="testpass123",
            role="student",
        )
        self.instructor = CustomUser.objects.create_user(
            username="instructor2",
            email="instructor2@example.com",
            password="testpass123",
            role="instructor",
        )

        # --- Course and assignment ---
        self.course = Course.objects.create(
            title="History 101", description="Intro to history", instructor=self.instructor
        )
        self.assignment = Assignment.objects.create(
            title="Essay", description="History essay", due_date="2026-02-01", course=self.course
        )

        # Authenticate as student using email
        url = reverse("token_obtain_pair")
        response = self.client.post(
            url, {"email": self.student.email, "password": "testpass123"}, format="json"
        )
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_create_submission(self):
        url = reverse("submission-list")
        data = {"assignment": self.assignment.id, "content": "My essay content"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Submission.objects.count(), 1)

    def test_list_submissions(self):
        Submission.objects.create(assignment=self.assignment, student=self.student, content="Draft essay")
        url = reverse("submission-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["student"]["email"], self.student.email)

    def test_unauthenticated_user_denied_access(self):
        self.client.credentials()  # Remove authentication
        url = reverse("submission-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_student_with_no_submissions_sees_empty_list(self):
        new_student = CustomUser.objects.create_user(
            username="student2", email="student2@example.com",
            password="testpass123", role="student"
        )
        url = reverse("token_obtain_pair")
        response = self.client.post(
            url, {"email": new_student.email, "password": "testpass123"}, format="json"
        )
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        url = reverse("submission-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_invalid_submission_missing_content(self):
        """
        Submission creation should fail if content is missing.
        """
        url = reverse("submission-list")
        data = {"assignment": self.assignment.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("content", response.data)

    def test_invalid_submission_wrong_assignment_id(self):
        """
        Submission creation should fail if assignment ID is invalid.
        """
        url = reverse("submission-list")
        data = {"assignment": 9999, "content": "Invalid assignment"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("assignment", response.data)
