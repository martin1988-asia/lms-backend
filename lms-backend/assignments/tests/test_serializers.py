from django.test import TestCase
from rest_framework.test import APIRequestFactory
from accounts.models import CustomUser
from courses.models import Course, Module
from assignments.models import Assignment, Submission
from assignments.serializers import AssignmentSerializer, SubmissionSerializer
from django.utils import timezone


class AssignmentSerializerTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.instructor = CustomUser.objects.create_user(
            email="inst@example.com", password="pass123", role="instructor", username="inst1"
        )
        self.course = Course.objects.create(title="Math 101", instructor=self.instructor)
        self.module = Module.objects.create(course=self.course, title="Intro", content="Basics")

    def test_create_sets_created_by_from_context(self):
        request = self.factory.post("/")
        request.user = self.instructor
        serializer = AssignmentSerializer(
            data={
                "title": "Homework",
                "course": self.course.id,
                "module": self.module.id,
                # use timezone-aware datetime to avoid warnings
                "due_date": (timezone.now() + timezone.timedelta(days=7)).isoformat()
            },
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        assignment = serializer.save()
        self.assertEqual(assignment.created_by, self.instructor)

    def test_to_representation_null_fields(self):
        assignment = Assignment.objects.create(
            title="Project",
            course=self.course,
            module=self.module,
            created_by=self.instructor,
            due_date=(timezone.now() + timezone.timedelta(days=14)).isoformat()
        )
        # Clear foreign keys safely without saving invalid state
        assignment.course_id = None
        assignment.module_id = None
        serializer = AssignmentSerializer(assignment)
        data = serializer.to_representation(assignment)
        self.assertIsNone(data.get("course_title"))
        self.assertIsNone(data.get("module_title"))


class SubmissionSerializerTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.instructor = CustomUser.objects.create_user(
            email="inst2@example.com", password="pass123", role="instructor", username="inst2"
        )
        self.student = CustomUser.objects.create_user(
            email="stud@example.com", password="pass123", role="student", username="stud1"
        )
        self.course = Course.objects.create(title="Physics 101", instructor=self.instructor)
        self.assignment = Assignment.objects.create(
            title="Lab Work",
            course=self.course,
            created_by=self.instructor,
            due_date=(timezone.now() + timezone.timedelta(days=21)).isoformat()
        )

    def test_create_sets_student_from_context(self):
        request = self.factory.post("/")
        request.user = self.student
        serializer = SubmissionSerializer(
            data={"assignment": self.assignment.id, "content": "My answer"},
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        submission = serializer.save()
        self.assertEqual(submission.student, self.student)

    def test_to_representation_null_assignment(self):
        submission = Submission.objects.create(
            assignment=self.assignment,
            student=self.student,
            content="Answer"
        )
        # Clear foreign key safely without saving invalid state
        submission.assignment_id = None
        serializer = SubmissionSerializer(submission)
        data = serializer.to_representation(submission)
        self.assertIsNone(data.get("assignment"))
