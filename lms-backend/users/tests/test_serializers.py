from django.test import TestCase
from accounts.models import CustomUser, Profile
from courses.models import Course, Module
from assignments.models import Assignment, Submission
from users.serializers import (
    ProfileSerializer,
    UserSerializer,
    CourseSerializer,
    ModuleSerializer,
    AssignmentSerializer,
    SubmissionSerializer,
)
from django.utils import timezone
import datetime


class ProfileSerializerTests(TestCase):
    def test_profile_serialization(self):
        user = CustomUser.objects.create_user(email="profile@example.com", password="pass123")
        # Ensure only one profile per user
        profile = Profile.objects.get(user=user)
        profile.bio = "Hello bio"
        profile.save()
        serializer = ProfileSerializer(profile)
        data = serializer.data
        self.assertEqual(data["bio"], "Hello bio")
        self.assertIn("avatar", data)


class UserSerializerTests(TestCase):
    def test_user_with_profile(self):
        user = CustomUser.objects.create_user(email="user@example.com", password="pass123", username="u1")
        profile = Profile.objects.get(user=user)
        profile.bio = "Bio text"
        profile.save()
        serializer = UserSerializer(user)
        data = serializer.data
        self.assertEqual(data["email"], "user@example.com")
        self.assertIsNotNone(data["profile"])

    def test_user_without_profile(self):
        user = CustomUser.objects.create_user(email="noprof@example.com", password="pass123", username="u2")
        serializer = UserSerializer(user)
        data = serializer.data
        # profile should still be present, but None
        self.assertIn("profile", data)


class CourseSerializerTests(TestCase):
    def setUp(self):
        self.instructor = CustomUser.objects.create_user(
            email="inst@example.com", password="pass123", role="instructor", username="inst1"
        )
        self.course = Course.objects.create(title="Math 101", description="Desc", instructor=self.instructor)

    def test_course_serialization(self):
        serializer = CourseSerializer(self.course)
        data = serializer.data
        self.assertEqual(data["instructor_name"], "inst1")


class ModuleSerializerTests(TestCase):
    def setUp(self):
        self.instructor = CustomUser.objects.create_user(
            email="inst2@example.com", password="pass123", role="instructor", username="inst2"
        )
        self.course = Course.objects.create(title="Physics 101", instructor=self.instructor)
        self.module = Module.objects.create(course=self.course, title="Intro", content="Basics")

    def test_module_serialization(self):
        serializer = ModuleSerializer(self.module)
        data = serializer.data
        # Ensure serializer exposes course title correctly
        self.assertEqual(data["course_title"], "Physics 101")


class AssignmentSerializerTests(TestCase):
    def setUp(self):
        self.instructor = CustomUser.objects.create_user(
            email="inst3@example.com", password="pass123", role="instructor", username="inst3"
        )
        self.course = Course.objects.create(title="Chemistry 101", instructor=self.instructor)
        self.assignment = Assignment.objects.create(
            course=self.course,
            title="Lab Work",
            description="Do experiments",
            due_date=timezone.now() + datetime.timedelta(days=3),
            created_by=self.instructor,
        )

    def test_assignment_serialization(self):
        serializer = AssignmentSerializer(self.assignment)
        data = serializer.data
        self.assertEqual(data["title"], "Lab Work")
        self.assertEqual(data["created_by_name"], "inst3")


class SubmissionSerializerTests(TestCase):
    def setUp(self):
        self.instructor = CustomUser.objects.create_user(
            email="inst4@example.com", password="pass123", role="instructor", username="inst4"
        )
        self.student = CustomUser.objects.create_user(
            email="stud@example.com", password="pass123", role="student", username="stud1"
        )
        self.course = Course.objects.create(title="Biology 101", instructor=self.instructor)
        self.assignment = Assignment.objects.create(
            course=self.course,
            title="Homework",
            due_date=timezone.now() + datetime.timedelta(days=5),
            created_by=self.instructor,
        )
        self.submission = Submission.objects.create(
            assignment=self.assignment,
            student=self.student,
            content="Answer",
            grade=90.0,
        )

    def test_submission_serialization(self):
        serializer = SubmissionSerializer(self.submission)
        data = serializer.data
        self.assertEqual(data["assignment_title"], "Homework")
        self.assertEqual(data["student_name"], "stud1")
