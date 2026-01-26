from django.test import TestCase
from accounts.models import CustomUser
from courses.models import Course, Module
from assignments.models import Assignment, Submission
import datetime
from django.utils import timezone


class AssignmentModelTests(TestCase):
    def setUp(self):
        self.instructor = CustomUser.objects.create_user(
            email="instructor@example.com", password="pass123", role="instructor", username="inst1"
        )
        self.course = Course.objects.create(title="Math 101", instructor=self.instructor)
        self.module = Module.objects.create(course=self.course, title="Intro", content="Basics")
        self.assignment = Assignment.objects.create(
            course=self.course,
            module=self.module,
            title="Homework",
            description="Solve problems",
            due_date=timezone.now() + datetime.timedelta(days=7),
            created_by=self.instructor,
        )

    def test_str_method(self):
        self.assertEqual(str(self.assignment), "Homework (Math 101)")

    def test_meta_verbose_names(self):
        self.assertEqual(str(Assignment._meta.verbose_name), "Assignment")
        self.assertEqual(str(Assignment._meta.verbose_name_plural), "Assignments")

    def test_meta_ordering(self):
        assignment2 = Assignment.objects.create(
            course=self.course,
            title="Project",
            due_date=timezone.now() + datetime.timedelta(days=10),
            created_by=self.instructor,
        )
        assignments = Assignment.objects.all()
        # ordering is by due_date
        self.assertEqual(list(assignments), [self.assignment, assignment2])

    def test_unique_assignment_per_course(self):
        with self.assertRaises(Exception):
            Assignment.objects.create(
                course=self.course,
                title="Homework",  # duplicate title for same course
                due_date=timezone.now() + datetime.timedelta(days=5),
                created_by=self.instructor,
            )


class SubmissionModelTests(TestCase):
    def setUp(self):
        self.instructor = CustomUser.objects.create_user(
            email="instructor2@example.com", password="pass123", role="instructor", username="inst2"
        )
        self.student = CustomUser.objects.create_user(
            email="student@example.com", password="pass123", role="student", username="stud1"
        )
        self.other_student = CustomUser.objects.create_user(
            email="student2@example.com", password="pass123", role="student", username="stud2"
        )
        self.course = Course.objects.create(title="Physics 101", instructor=self.instructor)
        self.assignment = Assignment.objects.create(
            course=self.course,
            title="Lab Work",
            due_date=timezone.now() + datetime.timedelta(days=3),
            created_by=self.instructor,
        )
        self.submission = Submission.objects.create(
            assignment=self.assignment,
            student=self.student,
            content="My answer",
            grade=95.0,
        )

    def test_str_method(self):
        self.assertEqual(str(self.submission), "stud1 → Lab Work")

    def test_meta_verbose_names(self):
        self.assertEqual(str(Submission._meta.verbose_name), "Submission")
        self.assertEqual(str(Submission._meta.verbose_name_plural), "Submissions")

    def test_meta_ordering(self):
        submission2 = Submission.objects.create(
            assignment=self.assignment,
            student=self.other_student,  # ✅ different student to avoid uniqueness conflict
            content="Another answer",
        )
        submissions = Submission.objects.all()
        # ordering is by -submitted_at, so latest submission2 comes first
        self.assertEqual(submissions[0], submission2)

    def test_unique_submission_per_student(self):
        with self.assertRaises(Exception):
            Submission.objects.create(
                assignment=self.assignment,
                student=self.student,
                content="Duplicate answer",
            )
