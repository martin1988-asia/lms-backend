from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import CustomUser
from courses.models import Course, Enrollment
from assignments.models import Assignment, Submission
from grades.models import Grade


class StudentAnalyticsTests(APITestCase):
    def setUp(self):
        # Create student and instructor
        self.student = CustomUser.objects.create_user(
            username="student1", email="student1@example.com",
            password="testpass123", role="student"
        )
        self.instructor = CustomUser.objects.create_user(
            username="instructor1", email="instructor1@example.com",
            password="testpass123", role="instructor"
        )
        # Course must have an instructor
        self.course = Course.objects.create(
            title="Science 101", description="Intro to science", instructor=self.instructor
        )
        Enrollment.objects.create(course=self.course, student=self.student)
        self.assignment = Assignment.objects.create(
            title="Lab Report", description="Write a lab report",
            due_date="2026-01-31", course=self.course
        )
        self.submission = Submission.objects.create(
            assignment=self.assignment, student=self.student, content="My lab report"
        )
        self.grade = Grade.objects.create(
            submission=self.submission, instructor=self.instructor,
            score=90, letter="A", feedback="Excellent"
        )

    def authenticate(self, user):
        url = reverse("token_obtain_pair")
        response = self.client.post(url, {"username": user.username, "password": "testpass123"})
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_student_analytics_returns_correct_gpa_and_completion_rate(self):
        self.authenticate(self.student)
        url = reverse("student-analytics")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["gpa"], 90.0)
        self.assertEqual(response.data["completion_rate"], 100.0)
        self.assertEqual(response.data["grades_count"], 1)
        self.assertEqual(response.data["assignments_count"], 1)


class InstructorAnalyticsTests(APITestCase):
    def setUp(self):
        self.instructor = CustomUser.objects.create_user(
            username="instructor2", email="instructor2@example.com",
            password="testpass123", role="instructor"
        )
        self.course = Course.objects.create(
            title="Math 101", description="Intro to math", instructor=self.instructor
        )
        self.assignment = Assignment.objects.create(
            title="Homework", description="Solve equations",
            due_date="2026-02-15", course=self.course
        )
        self.student = CustomUser.objects.create_user(
            username="student2", email="student2@example.com",
            password="testpass123", role="student"
        )
        Enrollment.objects.create(course=self.course, student=self.student)
        self.submission = Submission.objects.create(
            assignment=self.assignment, student=self.student, content="Equation solutions"
        )
        self.grade = Grade.objects.create(
            submission=self.submission, instructor=self.instructor,
            score=80, letter="B", feedback="Good effort"
        )

    def authenticate(self, user):
        url = reverse("token_obtain_pair")
        response = self.client.post(url, {"username": user.username, "password": "testpass123"})
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_instructor_analytics_returns_course_performance_and_counts(self):
        self.authenticate(self.instructor)
        url = reverse("instructor-analytics")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["courses_taught"], 1)
        self.assertEqual(response.data["assignments_created"], 1)
        self.assertEqual(response.data["submissions_received"], 1)
        self.assertEqual(response.data["grades_given"], 1)
        self.assertIn("Math 101", response.data["course_performance"])
        self.assertEqual(response.data["course_performance"]["Math 101"], 80.0)


class AdminAnalyticsTests(APITestCase):
    def setUp(self):
        self.admin = CustomUser.objects.create_user(
            username="admin1", email="admin1@example.com",
            password="testpass123", role="admin"
        )
        self.instructor = CustomUser.objects.create_user(
            username="instructor3", email="instructor3@example.com",
            password="testpass123", role="instructor"
        )
        self.student = CustomUser.objects.create_user(
            username="student3", email="student3@example.com",
            password="testpass123", role="student"
        )
        self.course = Course.objects.create(
            title="Science 101", description="Intro to science", instructor=self.instructor
        )
        Enrollment.objects.create(course=self.course, student=self.student)
        self.assignment = Assignment.objects.create(
            title="Lab Report", description="Write a lab report",
            due_date="2026-01-31", course=self.course
        )
        self.submission = Submission.objects.create(
            assignment=self.assignment, student=self.student, content="My lab report"
        )
        self.grade = Grade.objects.create(
            submission=self.submission, instructor=self.instructor,
            score=95, letter="A", feedback="Excellent"
        )

    def authenticate(self, user):
        url = reverse("token_obtain_pair")
        response = self.client.post(url, {"username": user.username, "password": "testpass123"})
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_admin_analytics_returns_global_stats(self):
        self.authenticate(self.admin)
        url = reverse("admin-analytics")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_courses"], 1)
        self.assertEqual(response.data["total_students"], 1)
        self.assertEqual(response.data["total_instructors"], 1)
        self.assertEqual(response.data["total_submissions"], 1)
        self.assertEqual(response.data["total_grades"], 1)
        self.assertEqual(response.data["global_gpa"], 95.0)
        self.assertIn("A", response.data["grade_distribution"])
        self.assertIn("Science 101", response.data["course_enrollment_stats"])
        self.assertEqual(response.data["course_enrollment_stats"]["Science 101"], 1)
