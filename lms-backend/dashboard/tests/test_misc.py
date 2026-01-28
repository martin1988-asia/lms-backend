from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import CustomUser
from courses.models import Course, Enrollment
from assignments.models import Assignment, Submission
from grades.models import Grade


class DashboardIsolationAndAccessTests(APITestCase):
    """
    Test suite for Student, Instructor, and Admin dashboards.
    Covers role-based isolation, field presence, denial cases, and edge scenarios.
    """
    def setUp(self):
        # --- Users ---
        self.instructor = CustomUser.objects.create_user(
            username="instructor1", email="instructor1@example.com",
            password="testpass123", role="instructor"
        )
        self.student = CustomUser.objects.create_user(
            username="student1", email="student1@example.com",
            password="testpass123", role="student"
        )
        self.admin = CustomUser.objects.create_user(
            username="admin1", email="admin1@example.com",
            password="testpass123", role="admin"
        )
        self.other_student = CustomUser.objects.create_user(
            username="student2", email="student2@example.com",
            password="testpass123", role="student"
        )
        self.other_instructor = CustomUser.objects.create_user(
            username="instructor2", email="instructor2@example.com",
            password="testpass123", role="instructor"
        )

        # --- Course, assignment, submission, grade for main student/instructor ---
        self.course = Course.objects.create(
            title="Science 101", description="Intro to science", instructor=self.instructor
        )
        Enrollment.objects.create(course=self.course, student=self.student)
        self.assignment = Assignment.objects.create(
            title="Lab Report", description="Write a lab report",
            due_date="2026-01-31", course=self.course
        )
        self.submission = Submission.objects.create(
            assignment=self.assignment, student=self.student, content="My lab report content"
        )
        self.grade = Grade.objects.create(
            submission=self.submission, instructor=self.instructor,
            score=92.5, letter="A-", feedback="Well done!"
        )

        # --- Course, assignment, submission for other student/instructor ---
        # ✅ Do NOT create a grade for other_student, so their dashboard is empty
        self.other_course = Course.objects.create(
            title="Math 101", description="Intro to math", instructor=self.other_instructor
        )
        Enrollment.objects.create(course=self.other_course, student=self.other_student)
        self.other_assignment = Assignment.objects.create(
            title="Homework", description="Solve equations",
            due_date="2026-02-15", course=self.other_course
        )
        self.other_submission = Submission.objects.create(
            assignment=self.other_assignment, student=self.other_student,
            content="Other student's homework"
        )
        # ❌ Removed self.other_grade creation

    def authenticate(self, user):
        """
        Helper method to authenticate a user via JWT using email.
        """
        url = reverse("token_obtain_pair")
        response = self.client.post(
            url, {"email": user.email, "password": "testpass123"}, format="json"
        )
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    # --- Student Dashboard ---
    def test_student_dashboard_fields(self):
        self.authenticate(self.student)
        response = self.client.get(reverse("student-dashboard"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for field in ["grades_count", "assignments_count", "gpa", "completion_rate"]:
            self.assertIn(field, response.data)

    def test_non_student_denied_student_dashboard(self):
        self.authenticate(self.instructor)
        response = self.client.get(reverse("student-dashboard"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_dashboard_empty_data(self):
        self.authenticate(self.other_student)
        response = self.client.get(reverse("student-dashboard"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["grades_count"], 0)   # ✅ now truly empty
        self.assertEqual(response.data["assignments_count"], 1)
        self.assertEqual(response.data["gpa"], 0.0)

    def test_student_dashboard_multiple_courses(self):
        second_course = Course.objects.create(
            title="Physics 101", description="Intro to physics", instructor=self.instructor
        )
        Enrollment.objects.create(course=second_course, student=self.student)
        self.authenticate(self.student)
        response = self.client.get(reverse("student-dashboard"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["assignments_count"], 1)

    # --- Instructor Dashboard ---
    def test_instructor_dashboard_fields(self):
        self.authenticate(self.instructor)
        response = self.client.get(reverse("instructor-dashboard"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for field in ["courses_taught", "assignments_created", "submissions_received", "grades_given", "course_performance"]:
            self.assertIn(field, response.data)

    def test_non_instructor_denied_instructor_dashboard(self):
        self.authenticate(self.student)
        response = self.client.get(reverse("instructor-dashboard"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_denied_instructor_dashboard(self):
        self.authenticate(self.admin)
        response = self.client.get(reverse("instructor-dashboard"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_instructor_dashboard_empty_data(self):
        self.authenticate(self.other_instructor)
        response = self.client.get(reverse("instructor-dashboard"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["courses_taught"], 1)
        self.assertEqual(response.data["assignments_created"], 1)
        self.assertEqual(response.data["submissions_received"], 1)
        self.assertEqual(response.data["grades_given"], 0)   # ✅ no grade created

    def test_instructor_dashboard_multiple_courses(self):
        second_course = Course.objects.create(
            title="Chemistry 101", description="Intro to chemistry", instructor=self.instructor
        )
        Assignment.objects.create(title="Chem Lab", description="Lab work", due_date="2026-03-01", course=second_course)
        self.authenticate(self.instructor)
        response = self.client.get(reverse("instructor-dashboard"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["courses_taught"], 2)

    # --- Admin Dashboard ---
    def test_admin_dashboard_fields(self):
        self.authenticate(self.admin)
        response = self.client.get(reverse("admin-dashboard"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for field in [
            "total_courses", "total_students", "total_instructors",
            "total_submissions", "total_grades", "global_gpa",
            "grade_distribution", "course_enrollment_stats"
        ]:
            self.assertIn(field, response.data)

    def test_non_admin_denied_admin_dashboard(self):
        self.authenticate(self.student)
        response = self.client.get(reverse("admin-dashboard"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_instructor_denied_admin_dashboard(self):
        self.authenticate(self.instructor)
        response = self.client.get(reverse("admin-dashboard"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_dashboard_empty_data(self):
        Course.objects.all().delete()
        Assignment.objects.all().delete()
        Submission.objects.all().delete()
        Grade.objects.all().delete()

        self.authenticate(self.admin)
        response = self.client.get(reverse("admin-dashboard"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_courses"], 0)
        self.assertEqual(response.data["total_students"], CustomUser.objects.filter(role="student").count())
        self.assertEqual(response.data["total_instructors"], CustomUser.objects.filter(role="instructor").count())
        self.assertEqual(response.data["total_submissions"], 0)
        self.assertEqual(response.data["total_grades"], 0)
        self.assertEqual(response.data["global_gpa"], 0.0)

    def test_admin_dashboard_multiple_courses(self):
        Course.objects.create(title="Philosophy 101", description="Intro to philosophy", instructor=self.instructor)
        Course.objects.create(title="Art 101", description="Intro to art", instructor=self.other_instructor)
        self.authenticate(self.admin)
        response = self.client.get(reverse("admin-dashboard"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["total_courses"], 2)
