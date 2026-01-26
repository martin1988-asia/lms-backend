from django.test import TestCase
from django.db import IntegrityError
from accounts.models import CustomUser
from courses.models import Course
from enrollments.models import Enrollment


class EnrollmentModelTests(TestCase):
    def setUp(self):
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
        self.course = Course.objects.create(title="Science 101", instructor=self.instructor)

    def test_str_representation(self):
        enrollment = Enrollment.objects.create(student=self.student, course=self.course)
        self.assertEqual(str(enrollment), "student1 enrolled in Science 101")

    def test_str_representation_with_missing_fields(self):
        # Simulate missing username and course title
        self.student.username = None
        self.student.save()
        self.course.title = None
        self.course.save()
        enrollment = Enrollment.objects.create(student=self.student, course=self.course)
        self.assertEqual(str(enrollment), "Unknown Student enrolled in Unknown Course")

    def test_unique_constraint(self):
        Enrollment.objects.create(student=self.student, course=self.course)
        with self.assertRaises(IntegrityError):
            Enrollment.objects.create(student=self.student, course=self.course)

    def test_ordering_by_enrolled_at(self):
        e1 = Enrollment.objects.create(student=self.student, course=self.course)
        e2 = Enrollment.objects.create(
            student=CustomUser.objects.create_user(
                email="student2@example.com",
                password="password123",
                role="student",
                username="student2"
            ),
            course=self.course
        )
        enrollments = list(Enrollment.objects.all())
        # Ordered by -enrolled_at, so latest enrollment comes first
        self.assertEqual(enrollments[0], e2)
        self.assertEqual(enrollments[1], e1)

    def test_meta_verbose_names(self):
        self.assertEqual(str(Enrollment._meta.verbose_name), "Enrollment")
        self.assertEqual(str(Enrollment._meta.verbose_name_plural), "Enrollments")
