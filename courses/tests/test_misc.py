from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import CustomUser
from courses.models import Course, Enrollment


class CourseTests(APITestCase):
    """
    Test suite for CourseViewSet.
    Covers instructor course creation, listing, and denial cases.
    """
    def setUp(self):
        self.instructor = CustomUser.objects.create_user(
            username="instructor1",
            email="instructor1@example.com",
            password="testpass123",
            role="instructor",
        )
        # Authenticate as instructor
        url = reverse("token_obtain_pair")
        response = self.client.post(
            url, {"email": self.instructor.email, "password": "testpass123"}, format="json"
        )
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

    def test_non_instructor_cannot_create_course(self):
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

        url = reverse("course-list")
        data = {"title": "Invalid", "description": "Should fail"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_course_missing_title(self):
        """
        Course creation should fail if required fields are missing.
        """
        url = reverse("course-list")
        data = {"description": "No title"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)


class EnrollmentTests(APITestCase):
    """
    Test suite for EnrollmentViewSet.
    Covers student enrollment creation, listing, and denial cases.
    """
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
        self.course = Course.objects.create(
            title="History 101", description="Intro to history", instructor=self.instructor
        )
        # Authenticate as student
        url = reverse("token_obtain_pair")
        response = self.client.post(
            url, {"email": self.student.email, "password": "testpass123"}, format="json"
        )
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_create_enrollment(self):
        url = reverse("enrollment-list")
        data = {"course": self.course.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Enrollment.objects.count(), 1)

        enrollment = Enrollment.objects.first()
        self.assertEqual(enrollment.student, self.student)
        self.assertEqual(enrollment.course, self.course)

    def test_list_enrollments(self):
        Enrollment.objects.create(student=self.student, course=self.course)
        url = reverse("enrollment-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["student"]["email"], self.student.email)

    def test_unauthenticated_user_denied_access(self):
        self.client.credentials()  # Remove authentication
        url = reverse("enrollment-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_instructor_cannot_enroll_students_directly(self):
        self.client.force_authenticate(user=self.instructor)
        url = reverse("enrollment-list")
        data = {"course": self.course.id, "student": self.student.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_with_no_enrollments_sees_empty_list(self):
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

        url = reverse("enrollment-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_duplicate_enrollment_prevention(self):
        """
        Students should not be able to enroll in the same course twice.
        """
        Enrollment.objects.create(student=self.student, course=self.course)
        url = reverse("enrollment-list")
        data = {"course": self.course.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_invalid_course_id_enrollment(self):
        """
        Enrollment creation should fail if course ID is invalid.
        """
        url = reverse("enrollment-list")
        data = {"course": 9999}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("course", response.data)
