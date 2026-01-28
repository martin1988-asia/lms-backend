from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import CustomUser
from courses.models import Course, Enrollment   # ✅ import Enrollment from courses.models


class EnrollmentTests(TestCase):
    """
    Test suite for EnrollmentViewSet.
    Covers role-based isolation for students, instructors, and admins,
    plus edge cases like invalid input and duplicate prevention.
    """
    def setUp(self):
        self.client = APIClient()

        # --- Users ---
        self.student = CustomUser.objects.create_user(
            email="student@example.com", password="password123", role="student"
        )
        self.instructor = CustomUser.objects.create_user(
            email="instructor@example.com", password="password123", role="instructor"
        )
        self.admin = CustomUser.objects.create_user(
            email="admin@example.com", password="password123", role="admin"
        )

        # --- Course taught by instructor ---
        self.course = Course.objects.create(
            title="Math 101", description="Basic Math", instructor=self.instructor
        )

        # --- Endpoint ---
        self.enrollment_url = reverse("enrollment-list")

    def test_student_can_enroll_in_course(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post(self.enrollment_url, {"course": self.course.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Enrollment.objects.count(), 1)

        enrollment = Enrollment.objects.first()
        self.assertEqual(enrollment.student, self.student)
        self.assertEqual(enrollment.course, self.course)

    def test_instructor_cannot_enroll_students_directly(self):
        self.client.force_authenticate(user=self.instructor)
        response = self.client.post(self.enrollment_url, {"course": self.course.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("detail", response.data)

    def test_admin_can_enroll_students(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            self.enrollment_url, {"course": self.course.id, "student": self.student.id}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Enrollment.objects.count(), 1)

    def test_student_can_list_own_enrollments(self):
        Enrollment.objects.create(student=self.student, course=self.course)
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.enrollment_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["student"]["email"], self.student.email)

    def test_instructor_can_list_course_enrollments(self):
        Enrollment.objects.create(student=self.student, course=self.course)
        self.client.force_authenticate(user=self.instructor)
        response = self.client.get(self.enrollment_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["course"], self.course.id)

    def test_admin_can_list_all_enrollments(self):
        Enrollment.objects.create(student=self.student, course=self.course)
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.enrollment_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_unauthenticated_user_denied_access(self):
        response = self.client.get(self.enrollment_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_student_with_no_enrollments_sees_empty_list(self):
        new_student = CustomUser.objects.create_user(
            email="student2@example.com", password="password123", role="student"
        )
        self.client.force_authenticate(user=new_student)
        response = self.client.get(self.enrollment_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_duplicate_enrollment_prevention(self):
        self.client.force_authenticate(user=self.student)
        Enrollment.objects.create(student=self.student, course=self.course)
        response = self.client.post(self.enrollment_url, {"course": self.course.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_invalid_course_id_enrollment(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post(self.enrollment_url, {"course": 9999})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("course", response.data)

    def test_admin_enrollment_invalid_student_id(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            self.enrollment_url, {"course": self.course.id, "student": 9999}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("student", response.data)
