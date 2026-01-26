from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from courses.models import Course, Module
from assignments.models import Assignment, Submission

User = get_user_model()


class UserTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",   # unique email
            password="admin123",
            role="admin",
        )
        self.client.force_authenticate(user=self.admin)

    def test_register_user(self):
        url = reverse("register")  # registration endpoint
        data = {
            "username": "student1",
            "email": "student1@example.com",
            "password": "test12345",
            "role": "student",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class CourseTests(APITestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username="teacher1",
            email="teacher1@example.com",
            password="teach123",
            role="instructor",
        )
        self.client.force_authenticate(user=self.teacher)

    def test_create_course(self):
        url = reverse("course-list")
        data = {
            "title": "Math 101",
            "description": "Intro Algebra",
            "instructor": self.teacher.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class ModuleTests(APITestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username="teacher2",
            email="teacher2@example.com",
            password="teach123",
            role="instructor",
        )
        self.course = Course.objects.create(
            title="Science",
            description="Physics",
            instructor=self.teacher,
        )
        self.client.force_authenticate(user=self.teacher)

    def test_create_module(self):
        url = reverse("module-list")
        data = {"course": self.course.id, "title": "Chapter 1", "content": "Basics"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class AssignmentTests(APITestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username="teacher3",
            email="teacher3@example.com",
            password="teach123",
            role="instructor",
        )
        self.course = Course.objects.create(
            title="English",
            description="Grammar",
            instructor=self.teacher,
        )
        self.module = Module.objects.create(
            course=self.course,
            title="Module A",
            content="Intro",
        )
        self.client.force_authenticate(user=self.teacher)

    def test_create_assignment(self):
        url = reverse("assignment-list")
        data = {
            "course": self.course.id,   # FIX: include course
            "module": self.module.id,
            "title": "Essay",
            "description": "Write an essay",
            "due_date": "2030-01-01T00:00:00Z",
            "created_by": self.teacher.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class SubmissionTests(APITestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username="teacher4",
            email="teacher4@example.com",   # FIX: unique email
            password="teach123",
            role="instructor",
        )
        self.student = User.objects.create_user(
            username="student2",
            email="student2@example.com",   # FIX: unique email
            password="stud123",
            role="student",
        )
        self.course = Course.objects.create(
            title="History",
            description="World Wars",
            instructor=self.teacher,
        )
        self.module = Module.objects.create(
            course=self.course,
            title="Module B",
            content="WWII",
        )
        self.assignment = Assignment.objects.create(
            course=self.course,   # FIX: include course
            module=self.module,
            title="Homework",
            description="Answer questions",
            due_date="2030-01-01T00:00:00Z",
            created_by=self.teacher,
        )
        self.client.force_authenticate(user=self.student)

    def test_create_submission(self):
        url = reverse("submission-list")
        data = {
            "assignment": self.assignment.id,
            "student": self.student.id,
            "content": "My answers",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
