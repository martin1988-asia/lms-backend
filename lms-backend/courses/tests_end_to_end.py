from django.test import TestCase
from rest_framework.test import APIClient
from accounts.models import CustomUser
from courses.models import Course, Enrollment
from assignments.models import Assignment, Submission
from django.utils import timezone


class EndToEndWorkflowTests(TestCase):
    """
    End-to-end integration tests for LMS workflows across accounts, courses, and assignments.
    """

    def setUp(self):
        self.client = APIClient()

        # Create users
        self.student = CustomUser.objects.create_user(
            username="student1", email="student@test.com", password="pass", role="student"
        )
        self.instructor = CustomUser.objects.create_user(
            username="instructor1", email="instructor@test.com", password="pass", role="instructor"
        )
        self.admin = CustomUser.objects.create_user(
            username="admin1", email="admin@test.com", password="pass", role="admin"
        )

        # Authenticate as instructor to create course
        self.client.force_authenticate(user=self.instructor)
        self.course = Course.objects.create(title="Math 101", instructor=self.instructor)

        # Instructor creates assignment
        self.assignment = Assignment.objects.create(
            course=self.course,
            title="Algebra Homework",
            due_date=timezone.now() + timezone.timedelta(days=7)
        )

        # Student enrolls in course
        Enrollment.objects.create(student=self.student, course=self.course)

        # Student submits assignment
        Submission.objects.create(
            assignment=self.assignment,
            student=self.student,
            submitted_at=timezone.now(),
            grade=85
        )

    # ---------------- Positive Flows ----------------

    def test_student_dashboard_flow(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get("/api/dashboard/student/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("gpa", data)
        self.assertEqual(data["assignments_count"], 1)
        self.assertGreaterEqual(data["gpa"], 85)

    def test_instructor_dashboard_flow(self):
        self.client.force_authenticate(user=self.instructor)
        response = self.client.get("/api/dashboard/instructor/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("course_performance", data)
        self.assertEqual(data["courses_taught"], 1)
        self.assertEqual(data["assignments_created"], 1)

    def test_admin_dashboard_flow(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/api/dashboard/admin/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total_students", data)
        self.assertIn("global_gpa", data)
        self.assertEqual(data["total_courses"], 1)

    def test_student_can_view_enrolled_courses(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get("/api/courses/enrolled/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["title"], "Math 101")

    def test_instructor_can_view_enrolled_students(self):
        self.client.force_authenticate(user=self.instructor)
        response = self.client.get(f"/api/courses/{self.course.id}/students/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["email"], "student@test.com")

    def test_admin_can_list_all_courses(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/api/courses/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(len(data), 1)

    # ---------------- Negative Cases ----------------

    def test_student_cannot_access_instructor_dashboard(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get("/api/dashboard/instructor/")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["detail"], "Access denied. Only instructors can view this dashboard.")

    def test_student_cannot_access_admin_dashboard(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get("/api/dashboard/admin/")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["detail"], "Access denied. Only admins can view this dashboard.")

    def test_instructor_cannot_access_student_dashboard(self):
        self.client.force_authenticate(user=self.instructor)
        response = self.client.get("/api/dashboard/student/")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["detail"], "Access denied. Only students can view this dashboard.")

    def test_instructor_cannot_access_admin_dashboard(self):
        self.client.force_authenticate(user=self.instructor)
        response = self.client.get("/api/dashboard/admin/")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["detail"], "Access denied. Only admins can view this dashboard.")

    def test_admin_cannot_access_student_dashboard(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/api/dashboard/student/")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["detail"], "Access denied. Only students can view this dashboard.")

    def test_admin_cannot_access_instructor_dashboard(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/api/dashboard/instructor/")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["detail"], "Access denied. Only instructors can view this dashboard.")
