from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import CustomUser
from courses.models import Course
from assignments.models import Assignment, Submission
from grades.models import Grade


class GradeTests(APITestCase):
    """
    Test suite for GradeViewSet.
    Covers instructor grade creation/listing, student grade isolation, authentication requirements,
    and edge cases like duplicate prevention, invalid input, and empty datasets.
    """
    def setUp(self):
        # --- Users ---
        self.instructor = CustomUser.objects.create_user(
            username="instructor1",
            email="instructor1@example.com",
            password="testpass123",
            role="instructor",
        )
        self.student = CustomUser.objects.create_user(
            username="student1",
            email="student1@example.com",
            password="testpass123",
            role="student",
        )

        # --- Course and assignment ---
        self.course = Course.objects.create(
            title="Math 101",
            description="Intro to math",
            instructor=self.instructor,
        )
        self.assignment = Assignment.objects.create(
            title="Homework 1",
            description="Solve equations",
            due_date="2026-01-31",
            course=self.course,
        )

        # --- Submission ---
        self.submission = Submission.objects.create(
            assignment=self.assignment,
            student=self.student,
            content="x + 2 = 4",
        )

        # --- Authenticate as instructor using email ---
        url = reverse("token_obtain_pair")
        response = self.client.post(
            url, {"email": self.instructor.email, "password": "testpass123"}, format="json"
        )
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_create_grade(self):
        url = reverse("grade-list")
        data = {
            "submission": self.submission.id,
            "score": "95.00",
            "letter": "A",
            "feedback": "Excellent work!",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Grade.objects.count(), 1)

        grade = Grade.objects.first()
        self.assertEqual(grade.instructor, self.instructor)
        self.assertEqual(grade.letter, "A")
        self.assertEqual(grade.feedback, "Excellent work!")

    def test_list_grades_as_instructor(self):
        Grade.objects.create(
            submission=self.submission,
            instructor=self.instructor,
            score=88.5,
            letter="B+",
            feedback="Good effort",
        )
        url = reverse("grade-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["letter"], "B+")

    def test_student_can_only_see_own_grades(self):
        Grade.objects.create(
            submission=self.submission,
            instructor=self.instructor,
            score=75.0,
            letter="C",
            feedback="Needs improvement",
        )
        # Authenticate as student
        url = reverse("token_obtain_pair")
        response = self.client.post(
            url, {"email": self.student.email, "password": "testpass123"}, format="json"
        )
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        url = reverse("grade-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["student"]["email"], self.student.email)

    def test_authentication_required(self):
        self.client.credentials()  # Remove credentials
        url = reverse("grade-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_duplicate_grade_prevention(self):
        Grade.objects.create(
            submission=self.submission,
            instructor=self.instructor,
            score=90.0,
            letter="A-",
            feedback="Solid work",
        )
        url = reverse("grade-list")
        data = {
            "submission": self.submission.id,
            "score": "85.00",
            "letter": "B",
            "feedback": "Second attempt",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_instructor_sees_multiple_grades(self):
        # ✅ Create a second assignment and submission so we can have multiple grades
        second_assignment = Assignment.objects.create(
            title="Homework 2",
            description="More equations",
            due_date="2026-02-01",
            course=self.course,
        )
        second_submission = Submission.objects.create(
            assignment=second_assignment,
            student=self.student,
            content="y - 3 = 2",
        )

        Grade.objects.create(
            submission=self.submission,
            instructor=self.instructor,
            score=70.0,
            letter="C-",
            feedback="Needs more work",
        )
        Grade.objects.create(
            submission=second_submission,
            instructor=self.instructor,
            score=85.0,
            letter="B",
            feedback="Improved",
        )
        url = reverse("grade-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

    def test_student_with_no_grades_sees_empty_list(self):
        new_student = CustomUser.objects.create_user(
            username="student2",
            email="student2@example.com",
            password="testpass123",
            role="student",
        )
        url = reverse("token_obtain_pair")
        response = self.client.post(
            url, {"email": new_student.email, "password": "testpass123"}, format="json"
        )
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        url = reverse("grade-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_invalid_score_rejected(self):
        """
        Grades with invalid score values should be rejected.
        """
        url = reverse("grade-list")
        data = {
            "submission": self.submission.id,
            "score": "invalid",  # not a number
            "letter": "A",
            "feedback": "Bad input",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("score", response.data)

    def test_non_instructor_cannot_create_grade(self):
        """
        Students should be denied grade creation.
        """
        # Authenticate as student
        url = reverse("token_obtain_pair")
        response = self.client.post(
            url, {"email": self.student.email, "password": "testpass123"}, format="json"
        )
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        url = reverse("grade-list")
        data = {
            "submission": self.submission.id,
            "score": "90.00",
            "letter": "A",
            "feedback": "Trying to grade",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
