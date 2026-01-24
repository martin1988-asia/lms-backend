from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import CustomUser
from courses.models import Course, Enrollment
from assignments.models import Assignment, Submission
from grades.models import Grade


class DashboardIsolationAndAccessTests(APITestCase):
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

        # --- Course, assignment, submission, grade for other student/instructor ---
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
        self.other_grade = Grade.objects.create(
            submission=self.other_submission, instructor=self.other_instructor,
            score=80, letter="B", feedback="Good effort"
        )

    def authenticate(self, user):
        url = reverse("token_obtain_pair")
        response = self.client.post(
            url, {"username": user.username, "password": "testpass123"}, format="json"
        )
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    # --- Assignments Isolation + Correctness ---
    def test_student_sees_only_assignments_from_enrolled_courses(self):
        self.authenticate(self.student)
        response = self.client.get(reverse("student-dashboard"))
        assignments = response.data["assignments"]
        self.assertEqual(assignments[0]["title"], "Lab Report")
        self.assertEqual(assignments[0]["description"], "Write a lab report")
        self.assertNotIn("Homework", [a["title"] for a in assignments])

    def test_instructor_sees_only_assignments_they_created(self):
        self.authenticate(self.instructor)
        response = self.client.get(reverse("instructor-dashboard"))
        assignments = response.data["assignments"]
        self.assertEqual(assignments[0]["title"], "Lab Report")
        self.assertEqual(assignments[0]["description"], "Write a lab report")
        self.assertNotIn("Homework", [a["title"] for a in assignments])

    def test_admin_sees_all_assignments(self):
        self.authenticate(self.admin)
        response = self.client.get(reverse("instructor-dashboard"))
        titles = [a["title"] for a in response.data["assignments"]]
        descriptions = [a["description"] for a in response.data["assignments"]]
        self.assertIn("Lab Report", titles)
        self.assertIn("Homework", titles)
        self.assertIn("Write a lab report", descriptions)
        self.assertIn("Solve equations", descriptions)
