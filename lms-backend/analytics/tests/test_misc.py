from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import CustomUser
from courses.models import Course, Enrollment
from assignments.models import Assignment, Submission
from grades.models import Grade


class AnalyticsTests(APITestCase):
    """
    Test suite for Student, Instructor, and Admin analytics endpoints.
    Covers role-based isolation, field presence, denial cases, and edge scenarios.
    """
    def setUp(self):
        # --- Users ---
        self.student = CustomUser.objects.create_user(
            username="student1", email="student1@example.com",
            password="testpass123", role="student"
        )
        self.instructor = CustomUser.objects.create_user(
            username="instructor1", email="instructor1@example.com",
            password="testpass123", role="instructor"
        )
        self.admin = CustomUser.objects.create_user(
            username="admin1", email="admin1@example.com",
            password="testpass123", role="admin"
        )

        # --- Course, assignment, submission, grade ---
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

    # --- Student Analytics ---
    def test_student_analytics_fields(self):
        self.authenticate(self.student)
        response = self.client.get(reverse("student-analytics"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for field in ["gpa", "completion_rate", "grades_count", "assignments_count"]:
            self.assertIn(field, response.data)

    def test_non_student_denied_student_analytics(self):
        self.authenticate(self.instructor)
        response = self.client.get(reverse("student-analytics"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_analytics_empty_data(self):
        new_student = CustomUser.objects.create_user(
            username="student2", email="student2@example.com",
            password="testpass123", role="student"
        )
        Enrollment.objects.create(course=self.course, student=new_student)
        self.authenticate(new_student)
        response = self.client.get(reverse("student-analytics"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["grades_count"], 0)
        self.assertEqual(response.data["gpa"], 0.0)

    def test_student_analytics_multiple_courses(self):
        """
        Students enrolled in multiple courses should see aggregated stats.
        """
        second_course = Course.objects.create(
            title="Physics 101", description="Intro to physics", instructor=self.instructor
        )
        Enrollment.objects.create(course=second_course, student=self.student)
        self.authenticate(self.student)
        response = self.client.get(reverse("student-analytics"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["assignments_count"], 1)

    # --- Instructor Analytics ---
    def test_instructor_analytics_fields(self):
        self.authenticate(self.instructor)
        response = self.client.get(reverse("instructor-analytics"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for field in ["courses_taught", "assignments_created", "submissions_received", "grades_given", "course_performance"]:
            self.assertIn(field, response.data)

    def test_non_instructor_denied_instructor_analytics(self):
        self.authenticate(self.student)
        response = self.client.get(reverse("instructor-analytics"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_instructor_analytics_empty_data(self):
        new_instructor = CustomUser.objects.create_user(
            username="instructor2", email="instructor2@example.com",
            password="testpass123", role="instructor"
        )
        self.authenticate(new_instructor)
        response = self.client.get(reverse("instructor-analytics"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["courses_taught"], 0)
        self.assertEqual(response.data["assignments_created"], 0)
        self.assertEqual(response.data["submissions_received"], 0)
        self.assertEqual(response.data["grades_given"], 0)

    def test_instructor_analytics_multiple_courses(self):
        """
        Instructors teaching multiple courses should see aggregated stats.
        """
        second_course = Course.objects.create(
            title="Chemistry 101", description="Intro to chemistry", instructor=self.instructor
        )
        Assignment.objects.create(title="Chem Lab", description="Lab work", due_date="2026-03-01", course=second_course)
        self.authenticate(self.instructor)
        response = self.client.get(reverse("instructor-analytics"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["courses_taught"], 2)

    # --- Admin Analytics ---
    def test_admin_analytics_fields(self):
        self.authenticate(self.admin)
        response = self.client.get(reverse("admin-analytics"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for field in [
            "total_courses", "total_students", "total_instructors",
            "total_submissions", "total_grades", "global_gpa",
            "grade_distribution", "course_enrollment_stats"
        ]:
            self.assertIn(field, response.data)

    def test_non_admin_denied_admin_analytics(self):
        self.authenticate(self.student)
        response = self.client.get(reverse("admin-analytics"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_analytics_empty_data(self):
        Course.objects.all().delete()
        Assignment.objects.all().delete()
        Submission.objects.all().delete()
        Grade.objects.all().delete()

        self.authenticate(self.admin)
        response = self.client.get(reverse("admin-analytics"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_courses"], 0)
        self.assertEqual(response.data["total_submissions"], 0)
        self.assertEqual(response.data["total_grades"], 0)
        self.assertEqual(response.data["global_gpa"], 0.0)

    def test_admin_analytics_multiple_courses(self):
        """
        Admins should see aggregated stats across multiple courses.
        """
        Course.objects.create(title="Philosophy 101", description="Intro to philosophy", instructor=self.instructor)
        Course.objects.create(title="Art 101", description="Intro to art", instructor=self.instructor)
        self.authenticate(self.admin)
        response = self.client.get(reverse("admin-analytics"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["total_courses"], 2)
