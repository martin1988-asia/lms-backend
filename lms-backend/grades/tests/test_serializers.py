from django.test import TestCase
from rest_framework import serializers
from rest_framework.test import APIRequestFactory
from accounts.models import CustomUser
from courses.models import Course
from assignments.models import Assignment, Submission
from grades.models import Grade
from grades.serializers import (
    UserNestedSerializer,
    AssignmentNestedSerializer,
    SubmissionNestedSerializer,
    GradeSerializer,
)
from django.utils import timezone


class NestedSerializerSmokeTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="nested@example.com",
            password="pass123",
            role="student",
            username="nested1"
        )
        self.instructor = CustomUser.objects.create_user(
            email="instnested@example.com",
            password="pass123",
            role="instructor",
            username="instnested"
        )
        self.course = Course.objects.create(
            title="History 101",
            instructor=self.instructor
        )
        self.assignment = Assignment.objects.create(
            course=self.course,
            title="Essay",
            due_date=(timezone.now() + timezone.timedelta(days=30)).isoformat(),
            created_by=self.instructor
        )

    def test_user_nested_serializer(self):
        serializer = UserNestedSerializer(self.user)
        data = serializer.data
        self.assertEqual(data["email"], "nested@example.com")
        self.assertEqual(data["role"], "student")

    def test_assignment_nested_serializer(self):
        serializer = AssignmentNestedSerializer(self.assignment)
        data = serializer.data
        self.assertEqual(data["title"], "Essay")
        self.assertIn("due_date", data)


class SubmissionNestedSerializerTests(TestCase):
    def setUp(self):
        self.instructor = CustomUser.objects.create_user(
            email="inst@example.com",
            password="pass123",
            role="instructor",
            username="inst1"
        )
        self.student = CustomUser.objects.create_user(
            email="stud@example.com",
            password="pass123",
            role="student",
            username="stud1"
        )
        self.course = Course.objects.create(
            title="Math 101",
            instructor=self.instructor
        )
        self.assignment = Assignment.objects.create(
            course=self.course,
            title="Homework",
            due_date=(timezone.now() + timezone.timedelta(days=7)).isoformat(),
            created_by=self.instructor
        )
        self.submission = Submission.objects.create(
            assignment=self.assignment,
            student=self.student,
            content="Answer"
        )

    def test_to_representation_with_student_and_assignment(self):
        serializer = SubmissionNestedSerializer(self.submission)
        data = serializer.data
        self.assertEqual(data["student"]["username"], "stud1")
        self.assertEqual(data["assignment"]["title"], "Homework")

    def test_to_representation_missing_student_and_assignment(self):
        # Clear foreign keys safely without saving invalid state
        self.submission.student_id = None
        self.submission.assignment_id = None
        serializer = SubmissionNestedSerializer(self.submission)
        data = serializer.to_representation(self.submission)
        self.assertIsNone(data.get("student"))
        self.assertIsNone(data.get("assignment"))


class GradeSerializerTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.instructor = CustomUser.objects.create_user(
            email="inst2@example.com",
            password="pass123",
            role="instructor",
            username="inst2"
        )
        self.student = CustomUser.objects.create_user(
            email="stud2@example.com",
            password="pass123",
            role="student",
            username="stud2"
        )
        self.course = Course.objects.create(
            title="Physics 101",
            instructor=self.instructor
        )
        self.assignment = Assignment.objects.create(
            course=self.course,
            title="Lab Work",
            due_date=(timezone.now() + timezone.timedelta(days=14)).isoformat(),
            created_by=self.instructor
        )
        self.submission = Submission.objects.create(
            assignment=self.assignment,
            student=self.student,
            content="Lab answer"
        )

    def test_get_student_returns_dict(self):
        grade = Grade.objects.create(
            submission=self.submission,
            instructor=self.instructor,
            score=90
        )
        serializer = GradeSerializer(grade)
        data = serializer.data
        self.assertEqual(data["student"]["username"], "stud2")

    def test_get_student_returns_none(self):
        # Clear foreign key safely without saving invalid state
        self.submission.student_id = None
        grade = Grade.objects.create(
            submission=self.submission,
            instructor=self.instructor,
            score=85
        )
        serializer = GradeSerializer(grade)
        data = serializer.data
        self.assertIsNone(data.get("student"))

    def test_validate_prevents_duplicate_grading(self):
        Grade.objects.create(
            submission=self.submission,
            instructor=self.instructor,
            score=80
        )
        serializer = GradeSerializer(data={"submission": self.submission.id, "score": 90})
        serializer.initial_data["submission"] = self.submission
        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_validate_allows_new_grade(self):
        # Use a different student to avoid duplicate submission constraint
        other_student = CustomUser.objects.create_user(
            email="otherstud@example.com",
            password="pass123",
            role="student",
            username="otherstud"
        )
        new_submission = Submission.objects.create(
            assignment=self.assignment,
            student=other_student,
            content="Another answer"
        )
        serializer = GradeSerializer(data={"submission": new_submission.id, "score": 88})
        serializer.initial_data["submission"] = new_submission
        self.assertTrue(serializer.is_valid())

    def test_create_sets_instructor_from_context(self):
        request = self.factory.post("/")
        request.user = self.instructor
        serializer = GradeSerializer(
            data={"submission": self.submission.id, "score": 95},
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        grade = serializer.save()
        self.assertEqual(grade.instructor, self.instructor)

    def test_update_sets_instructor_from_context(self):
        grade = Grade.objects.create(
            submission=self.submission,
            instructor=self.instructor,
            score=70
        )
        request = self.factory.put("/")
        request.user = self.instructor
        serializer = GradeSerializer(
            grade,
            data={"submission": self.submission.id, "score": 75},
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()
        self.assertEqual(updated.instructor, self.instructor)

    def test_to_representation_null_fields(self):
        grade = Grade.objects.create(
            submission=self.submission,
            instructor=self.instructor,
            score=88
        )
        # Clear foreign keys safely without saving invalid state
        grade.submission_id = None
        grade.instructor_id = None
        serializer = GradeSerializer(grade)
        data = serializer.to_representation(grade)
        self.assertIsNone(data.get("submission_detail"))
        self.assertIsNone(data.get("instructor"))
        self.assertIsNone(data.get("student"))

    def test_to_representation_student_missing_but_submission_exists(self):
        # Clear student foreign key safely without saving invalid state
        self.submission.student_id = None
        grade = Grade.objects.create(
            submission=self.submission,
            instructor=self.instructor,
            score=77
        )
        serializer = GradeSerializer(grade)
        data = serializer.to_representation(grade)
        self.assertIsNone(data.get("student"))
        self.assertIsNotNone(data.get("submission_detail"))
