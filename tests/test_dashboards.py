from datetime import timedelta
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import CustomUser
from courses.models import Course, Enrollment
from assignments.models import Assignment, Submission

class DashboardTests(APITestCase):
    def setUp(self):
        # Create users
        self.student = CustomUser.objects.create_user(
            username="student1", email="s1@test.com", password="pass", role="student"
        )
        self.instructor = CustomUser.objects.create_user(
            username="instructor1", email="i1@test.com", password="pass", role="instructor"
        )
        self.admin = CustomUser.objects.create_user(
            username="admin1", email="a1@test.com", password="pass", role="admin"
        )

        # Create course and assignment (must include due_date)
        self.course = Course.objects.create(title="Math 101", instructor=self.instructor)
        self.assignment = Assignment.objects.create(
            course=self.course,
            title="Test Assignment",
            due_date=timezone.now() + timedelta(days=7),
            created_by=self.instructor
        )

        # Enroll student in course
        Enrollment.objects.create(student=self.student, course=self.course)

        # Create submission with grade
        self.submission = Submission.objects.create(
            assignment=self.assignment,
            student=self.student,
            content="Answer",
            grade=85.0
        )

    # ---------------- STUDENT DASHBOARD ----------------
    def test_student_dashboard_values(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get("/api/dashboard/student/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data

        self.assertEqual(data["grades_count"], 1)
        self.assertEqual(data["assignments_count"], 1)
        self.assertEqual(data["gpa"], 85.0)
        self.assertEqual(data["completion_rate"], 100)
        self.assertIn("grade_distribution", data)
        self.assertIn("gpa_trend", data)

    # ---------------- INSTRUCTOR DASHBOARD ----------------
    def test_instructor_dashboard_values(self):
        self.client.force_authenticate(user=self.instructor)
        response = self.client.get("/api/dashboard/instructor/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data

        self.assertEqual(data["courses_taught"], 1)
        self.assertEqual(data["assignments_created"], 1)
        self.assertEqual(data["submissions_received"], 1)
        self.assertEqual(data["grades_given"], 1)
        self.assertIn("course_performance", data)
        self.assertIn("performance_trends", data)

    # ---------------- ADMIN DASHBOARD ----------------
    def test_admin_dashboard_values(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/api/dashboard/admin/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data

        self.assertEqual(data["total_courses"], 1)
        self.assertEqual(data["total_students"], 1)
        self.assertEqual(data["total_instructors"], 1)
        self.assertEqual(data["total_submissions"], 1)
        self.assertEqual(data["total_grades"], 1)
        self.assertEqual(data["global_gpa"], 85.0)
        self.assertIn("grade_distribution", data)
        self.assertIn("enrollment_trends", data)

    # ---------------- ROLE RESTRICTIONS ----------------
    def test_role_restrictions(self):
        self.client.force_authenticate(user=self.student)
        self.assertEqual(self.client.get("/api/dashboard/admin/").status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.instructor)
        self.assertEqual(self.client.get("/api/dashboard/student/").status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.admin)
        self.assertEqual(self.client.get("/api/dashboard/instructor/").status_code, status.HTTP_403_FORBIDDEN)
