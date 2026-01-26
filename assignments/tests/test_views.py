from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import CustomUser
from courses.models import Course, Enrollment
from assignments.models import Assignment, Submission
import datetime
from django.utils import timezone


class AssignmentSubmissionViewsTests(TestCase):
    """
    Comprehensive tests for assignments/views.py.
    Covers all branches: get_queryset for each role,
    create success/denial, and perform_create logic.
    """

    def setUp(self):
        self.client = APIClient()
        self.admin = CustomUser.objects.create_user(
            email="admin@example.com", password="password123", role="admin", username="admin1"
        )
        self.student = CustomUser.objects.create_user(
            email="student@example.com", password="password123", role="student", username="student1"
        )
        self.instructor = CustomUser.objects.create_user(
            email="instructor@example.com", password="password123", role="instructor", username="instructor1"
        )
        self.course = Course.objects.create(title="Math 101", instructor=self.instructor)
        Enrollment.objects.create(course=self.course, student=self.student)
        self.assignment = Assignment.objects.create(
            title="Homework",
            course=self.course,
            created_by=self.instructor,
            due_date=timezone.now() + datetime.timedelta(days=7)
        )

    # --- AssignmentViewSet ---
    def test_assignment_queryset_instructor(self):
        self.client.force_authenticate(user=self.instructor)
        response = self.client.get("/assignments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_assignment_queryset_student(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get("/assignments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_assignment_queryset_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/assignments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_assignment_queryset_no_role(self):
        user = CustomUser.objects.create_user(email="norole@example.com", password="password123", username="norole1")
        self.client.force_authenticate(user=user)
        response = self.client.get("/assignments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_assignment_queryset_unauthenticated(self):
        response = self.client.get("/assignments/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_assignment_create_instructor_success(self):
        self.client.force_authenticate(user=self.instructor)
        due_date = datetime.datetime(2026, 1, 31, 0, 0, tzinfo=datetime.timezone.utc)
        response = self.client.post("/assignments/", {
            "title": "New HW",
            "course": self.course.id,
            "due_date": due_date.isoformat()
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        assignment_id = response.data["id"]
        assignment = Assignment.objects.get(id=assignment_id)
        self.assertEqual(assignment.created_by, self.instructor)

    def test_assignment_create_student_denied(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post("/assignments/", {
            "title": "New HW",
            "course": self.course.id
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_assignment_create_admin_denied(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post("/assignments/", {
            "title": "New HW",
            "course": self.course.id
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- SubmissionViewSet ---
    def test_submission_queryset_student(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get("/submissions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_submission_queryset_instructor(self):
        self.client.force_authenticate(user=self.instructor)
        response = self.client.get("/submissions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_submission_queryset_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/submissions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_submission_queryset_no_role(self):
        user = CustomUser.objects.create_user(email="norole2@example.com", password="password123", username="norole2")
        self.client.force_authenticate(user=user)
        response = self.client.get("/submissions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_submission_queryset_unauthenticated(self):
        response = self.client.get("/submissions/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_submission_create_student_success(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post("/submissions/", {
            "assignment": self.assignment.id,
            "content": "My Answer"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        submission_id = response.data["id"]
        submission = Submission.objects.get(id=submission_id)
        self.assertEqual(submission.student, self.student)

    def test_submission_create_instructor_denied(self):
        self.client.force_authenticate(user=self.instructor)
        response = self.client.post("/submissions/", {
            "assignment": self.assignment.id,
            "content": "Answer"
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_submission_create_admin_denied(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post("/submissions/", {
            "assignment": self.assignment.id,
            "content": "Answer"
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
