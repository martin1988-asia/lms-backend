from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from courses.models import Course, Enrollment
from assignments.models import Assignment, Submission
from grades.models import Grade
from django.utils import timezone

User = get_user_model()


class GradesTests(TestCase):
    """
    Test suite for the Grades app.
    Covers grade creation, GPA aggregation, and role-based access.
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
        self.course = Course.objects.create(title="History 101", instructor=self.instructor)

        # Student enrolls
        Enrollment.objects.create(student=self.student, course=self.course)

        # Instructor creates assignment
        self.assignment = Assignment.objects.create(
            course=self.course, title="Essay", due_date=timezone.now() + timezone.timedelta(days=7)
        )

        # Student submits assignment
        self.submission = Submission.objects.create(
            assignment=self.assignment,
            student=self.student,
            submitted_at=timezone.now(),
            content="My essay"
        )

    # ---------------- Positive Flows ----------------

    def test_instructor_can_assign_grade(self):
        self.client.force_authenticate(user=self.instructor)
        payload = {"submission": self.submission.id, "score": 88}
        response = self.client.post("/api/grades/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        grade = Grade.objects.get(submission=self.submission)
        self.assertEqual(grade.score, 88)

    def test_student_can_view_own_grades(self):
        grade = Grade.objects.create(submission=self.submission, score=92)
        self.client.force_authenticate(user=self.student)
        response = self.client.get("/api/grades/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["score"], 92)

    def test_admin_can_view_all_grades(self):
        Grade.objects.create(submission=self.submission, score=75)
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/api/grades/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_gpa_calculation_for_student(self):
        Grade.objects.create(submission=self.submission, score=85)
        # Add another assignment + submission + grade
        assignment2 = Assignment.objects.create(
            course=self.course, title="Quiz", due_date=timezone.now() + timezone.timedelta(days=3)
        )
        submission2 = Submission.objects.create(
            assignment=assignment2, student=self.student, submitted_at=timezone.now(), content="Quiz answers"
        )
        Grade.objects.create(submission=submission2, score=95)

        self.client.force_authenticate(user=self.student)
        response = self.client.get("/api/grades/gpa/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("gpa", response.data)
        self.assertEqual(response.data["gpa"], 90)  # average of 85 and 95

    # ---------------- Negative Cases ----------------

    def test_student_cannot_assign_grade(self):
        self.client.force_authenticate(user=self.student)
        payload = {"submission": self.submission.id, "score": 100}
        response = self.client.post("/api/grades/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_instructor_cannot_view_other_students_grades_without_permission(self):
        other_student = User.objects.create_user(
            email="other@example.com", password="securePass123", username="other", role="student"
        )
        other_submission = Submission.objects.create(
            assignment=self.assignment, student=other_student, submitted_at=timezone.now(), content="Other essay"
        )
        Grade.objects.create(submission=other_submission, score=70)

        self.client.force_authenticate(user=self.instructor)
        response = self.client.get("/api/grades/")
        # Depending on your policy, instructors may only see grades for their own course.
        # Here we assert they cannot see unrelated grades.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        scores = [g["score"] for g in response.data]
        self.assertNotIn(70, scores)
