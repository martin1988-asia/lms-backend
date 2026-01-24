from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import CustomUser
from courses.models import Course, Enrollment


class CourseTests(APITestCase):
    def setUp(self):
        self.instructor = CustomUser.objects.create_user(
            username="instructor1",
            email="instructor1@example.com",
            password="testpass123",
            role="instructor",
        )
        # Get JWT token
        url = reverse("token_obtain_pair")
        response = self.client.post(url, {"username": "instructor1", "password": "testpass123"}, format="json")
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_create_course(self):
        url = reverse("course-list")
        data = {"title": "Math 101", "description": "Introductory math course"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 1)

    def test_list_courses(self):
        Course.objects.create(title="Science 101", description="Intro to science", instructor=self.instructor)
        url = reverse("course-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)


class EnrollmentTests(APITestCase):
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

        # Authenticate as student
        url = reverse("token_obtain_pair")
        response = self.client.post(url, {"username": "student1", "password": "testpass123"}, format="json")
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_create_enrollment(self):
        url = reverse("enrollment-list")
        data = {"course": self.course.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Enrollment.objects.count(), 1)

    def test_list_enrollments(self):
        Enrollment.objects.create(student=self.student, course=self.course)
        url = reverse("enrollment-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
