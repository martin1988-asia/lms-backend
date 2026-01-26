from django.test import TestCase
from accounts.models import CustomUser
from courses.models import Course, Enrollment, Module


class CourseModelTests(TestCase):
    def setUp(self):
        self.instructor = CustomUser.objects.create_user(
            email="instructor@example.com",
            password="pass123",
            role="instructor",
            username="inst1"
        )
        self.course = Course.objects.create(
            title="Math 101",
            instructor=self.instructor
        )

    def test_str_method(self):
        self.assertEqual(str(self.course), "Math 101 (Instructor: inst1)")

    def test_meta_verbose_names(self):
        self.assertEqual(str(Course._meta.verbose_name), "Course")
        self.assertEqual(str(Course._meta.verbose_name_plural), "Courses")

    def test_meta_ordering(self):
        course2 = Course.objects.create(
            title="Biology 101",
            instructor=self.instructor
        )
        courses = Course.objects.all()
        # ordering is by title
        self.assertEqual(list(courses), [course2, self.course])


class EnrollmentModelTests(TestCase):
    def setUp(self):
        self.student = CustomUser.objects.create_user(
            email="student@example.com",
            password="pass123",
            role="student",
            username="stud1"
        )
        self.other_student = CustomUser.objects.create_user(
            email="student2@example.com",
            password="pass123",
            role="student",
            username="stud2"
        )
        self.instructor = CustomUser.objects.create_user(
            email="instructor@example.com",
            password="pass123",
            role="instructor",
            username="inst1"
        )
        self.course = Course.objects.create(
            title="Physics 101",
            instructor=self.instructor
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course
        )

    def test_str_method(self):
        self.assertEqual(str(self.enrollment), "stud1 enrolled in Physics 101")

    def test_meta_verbose_names(self):
        self.assertEqual(str(Enrollment._meta.verbose_name), "Enrollment")
        self.assertEqual(str(Enrollment._meta.verbose_name_plural), "Enrollments")

    def test_meta_ordering(self):
        # use a different student to avoid unique constraint violation
        enrollment2 = Enrollment.objects.create(
            student=self.other_student,
            course=self.course
        )
        enrollments = Enrollment.objects.all()
        # ordering is by -date_enrolled, so latest enrollment2 comes first
        self.assertEqual(enrollments[0], enrollment2)

    def test_unique_together_constraint(self):
        with self.assertRaises(Exception):
            Enrollment.objects.create(
                student=self.student,
                course=self.course
            )


class ModuleModelTests(TestCase):
    def setUp(self):
        self.instructor = CustomUser.objects.create_user(
            email="instructor2@example.com",
            password="pass123",
            role="instructor",
            username="inst2"
        )
        self.course = Course.objects.create(
            title="Chemistry 101",
            instructor=self.instructor
        )
        self.module = Module.objects.create(
            course=self.course,
            title="Intro",
            content="Basics"
        )

    def test_str_method(self):
        self.assertEqual(str(self.module), "Intro (Chemistry 101)")

    def test_meta_verbose_names(self):
        self.assertEqual(str(Module._meta.verbose_name), "Module")
        self.assertEqual(str(Module._meta.verbose_name_plural), "Modules")

    def test_meta_ordering(self):
        module2 = Module.objects.create(
            course=self.course,
            title="Advanced",
            content="Details"
        )
        modules = Module.objects.all()
        # ordering is by title
        self.assertEqual(list(modules), [module2, self.module])
