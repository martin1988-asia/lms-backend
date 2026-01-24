from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import CustomUser
from courses.models import Course
from assignments.models import Assignment, Submission
from grades.models import Grade


class GradeTests(APITestCase):
    def setUp(self):
        # Create instructor and student
        self.instructor = CustomUser.objects.create_user(
            username="instructor1",
            email="instructor1@example.com",
            password="testpass123",
            role="instructor",
        )
        self.student = CustomUser.objects.create_user(
            username="student1",
            email="student1@example.com",
            password="testpass123",
            role="student",
        )

        # Create course and assignment
        self.course = Course.objects.create(
            title="Math 101",
            description="Intro to math",
            instructor=self.instructor,
        )
        self.assignment = Assignment.objects.create(
            title="Homework 1",
            description="Solve equations",
            due_date="2026-01-31",
            course=self.course,
        )

        # Create submission
        self.submission = Submission.objects.create(
            assignment=self.assignment,
            student=self.student,
            content="x + 2 = 4",
        )

        # Authenticate as instructor
        url = reverse("token_obtain_pair")
        response = self.client.post(
            url, {"username": "instructor1", "password": "testpass123"}, format="json"
        )
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_create_grade(self):
        url = reverse("grade-list")
        data = {
            "submission": self.submission.id,
            "score": "95.00",
            "letter": "A",
            "feedback": "Excellent work!",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Grade.objects.count(), 1)

    def test_list_grades(self):
        Grade.objects.create(
            submission=self.submission,
            instructor=self.instructor,
            score=88.5,
            letter="B+",
            feedback="Good effort",
        )
        url = reverse("grade-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_authentication_required(self):
        # Remove credentials
        self.client.credentials()
        url = reverse("grade-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
