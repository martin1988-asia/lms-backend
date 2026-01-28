from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import CustomUser
from courses.models import Course
from enrollments.models import Enrollment
from assignments.models import Assignment, Submission
from grades.models import Grade


class AnalyticsViewsTests(TestCase):
    """
    Comprehensive tests for analytics/views.py.
    Covers list() for each role, explicit role-based endpoints,
    and admin analytics content.
    """

    def setUp(self):
        self.client = APIClient()
        self.admin = CustomUser.objects.create_user(
            email="admin@example.com", password="password123", role="admin"
        )
        self.student = CustomUser.objects.create_user(
            email="student@example.com", password="password123", role="student"
        )
        self.instructor = CustomUser.objects.create_user(
            email="instructor@example.com", password="password123", role="instructor"
        )
        self.course = Course.objects.create(title="Math 101", instructor=self.instructor)
        Enrollment.objects.create(course=self.course, student=self.student)
        self.assignment = Assignment.objects.create(
            title="Homework",
            course=self.course,
            created_by=self.instructor,
            due_date="2026-01-30T00:00:00Z"
        )
        self.submission = Submission.objects.create(
            student=self.student, assignment=self.assignment, content="Answer"
        )
        self.grade = Grade.objects.create(
            submission=self.submission, instructor=self.instructor, score=85, letter="B"
        )

    # --- list() method ---
    def test_list_student_role(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get("/analytics/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("gpa", response.data)

    def test_list_instructor_role(self):
        self.client.force_authenticate(user=self.instructor)
        response = self.client.get("/analytics/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("courses_taught", response.data)

    def test_list_admin_role(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/analytics/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_courses", response.data)

    def test_list_invalid_role(self):
        user = CustomUser.objects.create_user(email="norole@example.com", password="password123")
        self.client.force_authenticate(user=user)
        response = self.client.get("/analytics/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- Explicit role-based endpoints ---
    def test_student_endpoint_success(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get("/analytics/student/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("gpa", response.data)

    def test_student_endpoint_denied_for_non_student(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/analytics/student/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_instructor_endpoint_success(self):
        self.client.force_authenticate(user=self.instructor)
        response = self.client.get("/analytics/instructor/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("courses_taught", response.data)

    def test_instructor_endpoint_denied_for_non_instructor(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get("/analytics/instructor/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_endpoint_success(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/analytics/admin/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_courses", response.data)

    def test_admin_endpoint_denied_for_non_admin(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get("/analytics/admin/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- Admin analytics content ---
    def test_admin_analytics_includes_grade_distribution(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/analytics/admin/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("grade_distribution", response.data)
        self.assertIn("B", response.data["grade_distribution"])

    def test_admin_analytics_empty_grades(self):
        Grade.objects.all().delete()
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/analytics/admin/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["global_gpa"], 0.0)
        self.assertEqual(response.data["grade_distribution"], {})

    def test_admin_analytics_course_enrollment_stats(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/analytics/admin/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.course.title, response.data["course_enrollment_stats"])

    # --- Edge cases for student/instructor analytics ---
    def test_student_analytics_no_assignments(self):
        Assignment.objects.all().delete()
        Submission.objects.all().delete()
        Grade.objects.all().delete()
        self.client.force_authenticate(user=self.student)
        response = self.client.get("/analytics/student/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["completion_rate"], 0.0)

    def test_instructor_analytics_no_courses(self):
        Course.objects.all().delete()
        self.client.force_authenticate(user=self.instructor)
        response = self.client.get("/analytics/instructor/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["course_performance"], {})
