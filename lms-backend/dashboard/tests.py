from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from courses.models import Course, Enrollment
from assignments.models import Assignment, Submission
from grades.models import Grade
from django.utils import timezone

User = get_user_model()


class DashboardTests(TestCase):
    """
    Test suite for the Dashboard app.
    Covers student, instructor, and admin analytics endpoints.
    """

    def setUp(self):
        self.client = APIClient()

        # Create users
        self.student = User.objects.create_user(
            email="student@example.com", password="securePass123", username="student", role="student"
        )
        self.instructor = User.objects.create_user(
            email="instructor@example.com", password="securePass123", username="instructor", role="instructor"
        )
        self.admin = User.objects.create_superuser(
            email="admin@example.com", password="securePass123", username="admin"
        )

        # Instructor creates course
        self.course = Course.objects.create(title="Physics 101", instructor=self.instructor)

        # Student enrolls
        Enrollment.objects.create(student=self.student, course=self.course)

        # Instructor creates assignment
        self.assignment = Assignment.objects.create(
            course=self.course, title="Lab Report", due_date=timezone.now() + timezone.timedelta(days=7)
        )

        # Student submits assignment
        self.submission = Submission.objects.create(
            assignment=self.assignment,
            student=self.student,
            submitted_at=timezone.now(),
            content="Lab work"
        )

        # Instructor grades submission
        Grade.objects.create(submission=self.submission, score=90)

    # ---------------- Student Dashboard ----------------

    def test_student_dashboard_returns_correct_metrics(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get("/api/dashboard/student/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("gpa", data)
        self.assertEqual(data["gpa"], 90)
        self.assertEqual(data["assignments_count"], 1)
        self.assertEqual(data["courses_enrolled"], 1)

    # ---------------- Instructor Dashboard ----------------

    def test_instructor_dashboard_returns_correct_metrics(self):
        self.client.force_authenticate(user=self.instructor)
        response = self.client.get("/api/dashboard/instructor/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("course_performance", data)
        self.assertEqual(data["courses_taught"], 1)
        self.assertEqual(data["assignments_created"], 1)

    # ---------------- Admin Dashboard ----------------

    def test_admin_dashboard_returns_correct_metrics(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/api/dashboard/admin/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("total_students", data)
        self.assertIn("global_gpa", data)
        self.assertEqual(data["total_courses"], 1)

    # ---------------- Negative Cases ----------------

    def test_student_cannot_access_instructor_dashboard(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get("/api/dashboard/instructor/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_cannot_access_admin_dashboard(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get("/api/dashboard/admin/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_instructor_cannot_access_student_dashboard(self):
        self.client.force_authenticate(user=self.instructor)
        response = self.client.get("/api/dashboard/student/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_cannot_access_student_dashboard(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/api/dashboard/student/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_cannot_access_instructor_dashboard(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/api/dashboard/instructor/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
