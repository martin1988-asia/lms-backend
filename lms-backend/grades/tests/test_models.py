from django.test import TestCase
from accounts.models import CustomUser
from courses.models import Course
from assignments.models import Assignment, Submission
from grades.models import Grade
from django.utils import timezone
import datetime


class GradeModelTests(TestCase):
    def setUp(self):
        self.instructor = CustomUser.objects.create_user(
            email="instructor@example.com",
            password="pass123",
            role="instructor",
            username="instructor1"
        )
        self.student = CustomUser.objects.create_user(
            email="student@example.com",
            password="pass123",
            role="student",
            username="student1"
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

    def test_str_method_with_letter(self):
        grade = Grade.objects.create(
            submission=self.submission,
            instructor=self.instructor,
            letter="A"
        )
        self.assertEqual(str(grade), "student1 → A")

    def test_str_method_with_score(self):
        grade = Grade.objects.create(
            submission=self.submission,
            instructor=self.instructor,
            score=95.5
        )
        self.assertEqual(str(grade), "student1 → 95.5")

    def test_save_updates_submission_grade(self):
        Grade.objects.create(
            submission=self.submission,
            instructor=self.instructor,
            score=88.0
        )
        self.submission.refresh_from_db()
        self.assertEqual(self.submission.grade, 88.0)

    def test_save_does_not_update_submission_when_score_none(self):
        Grade.objects.create(
            submission=self.submission,
            instructor=self.instructor,
            score=None,
            letter="B"
        )
        self.submission.refresh_from_db()
        # grade field on submission should remain None
        self.assertIsNone(self.submission.grade)

    def test_meta_verbose_names(self):
        self.assertEqual(str(Grade._meta.verbose_name), "Grade")
        self.assertEqual(str(Grade._meta.verbose_name_plural), "Grades")

    def test_meta_ordering(self):
        # Create a second student and submission so each grade is unique
        student2 = CustomUser.objects.create_user(
            email="student2@example.com",
            password="pass123",
            role="student",
            username="student2"
        )
        submission2 = Submission.objects.create(
            student=student2,
            assignment=self.assignment,
            content="Another Answer"
        )
        grade1 = Grade.objects.create(
            submission=self.submission,
            instructor=self.instructor,
            score=70.0
        )
        grade2 = Grade.objects.create(
            submission=submission2,
            instructor=self.instructor,
            score=90.0
        )
        grades = Grade.objects.all()
        # ordering is by -graded_at, so latest grade2 comes first
        self.assertEqual(grades[0], grade2)
