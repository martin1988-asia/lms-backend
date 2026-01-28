from django.test import TestCase
from rest_framework import serializers
from rest_framework.test import APIRequestFactory
from accounts.models import CustomUser
from courses.models import Course, Enrollment
from courses.serializers import CourseSerializer, EnrollmentSerializer


class CourseSerializerTests(TestCase):
    def setUp(self):
        self.instructor = CustomUser.objects.create_user(
            email="inst@example.com",
            password="pass123",
            role="instructor",
            username="inst1"
        )
        self.course = Course.objects.create(
            title="Math 101",
            description="Desc",
            instructor=self.instructor
        )

    def test_to_representation_with_instructor(self):
        serializer = CourseSerializer(self.course)
        data = serializer.data
        self.assertEqual(data["instructor"]["username"], "inst1")

    def test_to_representation_without_instructor(self):
        # Clear foreign key safely without saving invalid state
        self.course.instructor_id = None
        serializer = CourseSerializer(self.course)
        data = serializer.to_representation(self.course)
        # Use .get() to avoid KeyError if field omitted
        self.assertIsNone(data.get("instructor"))


class EnrollmentSerializerTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.student = CustomUser.objects.create_user(
            email="stud@example.com",
            password="pass123",
            role="student",
            username="stud1"
        )
        self.instructor = CustomUser.objects.create_user(
            email="inst2@example.com",
            password="pass123",
            role="instructor",
            username="inst2"
        )
        self.course = Course.objects.create(
            title="Physics 101",
            instructor=self.instructor
        )

    def test_validate_prevents_duplicate_enrollment(self):
        Enrollment.objects.create(student=self.student, course=self.course)
        request = self.factory.post("/")
        request.user = self.student
        serializer = EnrollmentSerializer(
            data={"course": self.course.id},
            context={"request": request},
        )
        # simulate passing the actual course object to trigger duplicate check
        serializer.initial_data["course"] = self.course
        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_create_sets_student_from_context(self):
        request = self.factory.post("/")
        request.user = self.student
        serializer = EnrollmentSerializer(
            data={"course": self.course.id},
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        enrollment = serializer.save()
        self.assertEqual(enrollment.student, self.student)

    def test_to_representation_null_fields(self):
        enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course
        )
        # Clear foreign keys safely without saving invalid state
        enrollment.course_id = None
        enrollment.student_id = None
        serializer = EnrollmentSerializer(enrollment)
        data = serializer.to_representation(enrollment)
        self.assertIsNone(data.get("course"))
        self.assertIsNone(data.get("student"))
