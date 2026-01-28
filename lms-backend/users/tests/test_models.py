from django.test import TestCase
from accounts.models import CustomUser
from users.models import StudentProfile, InstructorProfile, AdminProfile


class StudentProfileTests(TestCase):
    def setUp(self):
        self.student = CustomUser.objects.create_user(
            email="student@example.com", password="pass123", role="student", username="stud1"
        )

    def test_str_method(self):
        self.assertEqual(str(self.student.student_profile), "StudentProfile for stud1")

    def test_signal_creates_student_profile(self):
        self.assertIsInstance(self.student.student_profile, StudentProfile)

    def test_signal_updates_student_profile_on_save(self):
        self.student.student_profile.major = "Math"
        self.student.save()
        self.student.refresh_from_db()
        self.assertEqual(self.student.student_profile.major, "Math")


class InstructorProfileTests(TestCase):
    def setUp(self):
        self.instructor = CustomUser.objects.create_user(
            email="instructor@example.com", password="pass123", role="instructor", username="inst1"
        )

    def test_str_method(self):
        self.assertEqual(str(self.instructor.instructor_profile), "InstructorProfile for inst1")

    def test_signal_creates_instructor_profile(self):
        self.assertIsInstance(self.instructor.instructor_profile, InstructorProfile)

    def test_signal_updates_instructor_profile_on_save(self):
        self.instructor.instructor_profile.department = "Science"
        self.instructor.save()
        self.instructor.refresh_from_db()
        self.assertEqual(self.instructor.instructor_profile.department, "Science")


class AdminProfileTests(TestCase):
    def setUp(self):
        self.admin = CustomUser.objects.create_user(
            email="admin@example.com", password="pass123", role="admin", username="admin1"
        )

    def test_str_method(self):
        self.assertEqual(str(self.admin.admin_profile), "AdminProfile for admin1")

    def test_signal_creates_admin_profile(self):
        self.assertIsInstance(self.admin.admin_profile, AdminProfile)

    def test_signal_updates_admin_profile_on_save(self):
        self.admin.admin_profile.office = "HQ"
        self.admin.save()
        self.admin.refresh_from_db()
        self.assertEqual(self.admin.admin_profile.office, "HQ")
