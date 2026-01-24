from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import CustomUser
from courses.models import Course
from assignments.models import Assignment, Submission


class AssignmentTests(APITestCase):
    def setUp(self):
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
        # Authenticate as instructor
        url = reverse("token_obtain_pair")
        response = self.client.post(url, {"username": "instructor1", "password": "testpass123"}, format="json")
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_create_assignment(self):
        url = reverse("assignment-list")
        data = {"title": "Lab Report", "description": "Write a lab report", "due_date": "2026-01-31", "course": self.course.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Assignment.objects.count(), 1)

    def test_list_assignments(self):
        Assignment.objects.create(title="Essay", description="Write an essay", due_date="2026-02-01", course=self.course)
        url = reverse("assignment-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)


class SubmissionTests(APITestCase):
    def setUp(self):
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
        self.course = Course.objects.create(title="History 101", description="Intro to history", instructor=self.instructor)
        self.assignment = Assignment.objects.create(title="Essay", description="History essay", due_date="2026-02-01", course=self.course)

        # Authenticate as student
        url = reverse("token_obtain_pair")
        response = self.client.post(url, {"username": "student1", "password": "testpass123"}, format="json")
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
