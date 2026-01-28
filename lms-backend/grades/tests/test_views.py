from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import CustomUser
from courses.models import Course
from assignments.models import Assignment, Submission
from grades.models import Grade
from django.utils import timezone
import datetime


class GradeViewSetTests(TestCase):
    """
    Comprehensive tests for grades/views.py (GradeViewSet).
    Covers get_queryset for each role, create success/denial,
    and perform_create logic.
    """

    def setUp(self):
        self.client = APIClient()
        self.admin = CustomUser.objects.create_user(
            email="admin@example.com",
            password="password123",
            role="admin",
            username="admin1"
        )
        self.student = CustomUser.objects.create_user(
            email="student@example.com",
            password="password123",
            role="student",
            username="student1"
        )
        self.instructor = CustomUser.objects.create_user(
            email="instructor@example.com",
            password="password123",
            role="instructor",
            username="instructor1"
        )
        self.course = Course.objects.create(
            title="Math 101",
            instructor=self.instructor
        )
        self.assignment = Assignment.objects.create(
            title="Homework",
            course=self.course,
            created_by=self.instructor,
            due_date=timezone.now() + datetime.timedelta(days=7)  # ✅ ensure due_date is set
        )
        self.submission = Submission.objects.create(
            student=self.student,
            assignment=self.assignment,
            content="Answer"
        )
        self.grade = Grade.objects.create(
            submission=self.submission,
            instructor=self.instructor,
            score=85
        )

    # --- get_queryset ---
    def test_get_queryset_student_role(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get("/grades/grades/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for g in response.data:
            self.assertEqual(g["student"]["id"], self.student.id)

    def test_get_queryset_instructor_role(self):
        self.client.force_authenticate(user=self.instructor)
        response = self.client.get("/grades/grades/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for g in response.data:
            # ensure the assignment belongs to the instructor's course
            self.assertEqual(g["submission_detail"]["assignment"]["course"], self.course.id)

    def test_get_queryset_admin_role(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/grades/grades/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_get_queryset_user_without_role(self):
        user = CustomUser.objects.create_user(
            email="norole@example.com",
            password="password123",
            username="norole1"
        )
        self.client.force_authenticate(user=user)
        response = self.client.get("/grades/grades/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_get_queryset_user_with_invalid_role(self):
        user = CustomUser.objects.create_user(
            email="invalid@example.com",
            password="password123",
            role="ghost",
            username="ghost1"
        )
        self.client.force_authenticate(user=user)
        response = self.client.get("/grades/grades/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    # --- create ---
    def test_create_grade_instructor_success(self):
        self.client.force_authenticate(user=self.instructor)
        response = self.client.post("/grades/grades/", {
            "submission": self.submission.id,
            "score": 90
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        grade_id = response.data["id"]
        grade = Grade.objects.get(id=grade_id)
        self.assertEqual(grade.instructor, self.instructor)

    def test_create_grade_admin_success(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post("/grades/grades/", {
            "submission": self.submission.id,
            "score": 92
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_grade_student_denied(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post("/grades/grades/", {
            "submission": self.submission.id,
            "score": 75
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_grade_user_without_role_denied(self):
        user = CustomUser.objects.create_user(
            email="norole2@example.com",
            password="password123",
            username="norole2"
        )
        self.client.force_authenticate(user=user)
        response = self.client.post("/grades/grades/", {
            "submission": self.submission.id,
            "score": 80
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- perform_create ---
    def test_perform_create_sets_instructor(self):
        self.client.force_authenticate(user=self.instructor)
        response = self.client.post("/grades/grades/", {
            "submission": self.submission.id,
            "score": 99
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        grade_id = response.data["id"]
        grade = Grade.objects.get(id=grade_id)
        self.assertEqual(grade.instructor, self.instructor)
