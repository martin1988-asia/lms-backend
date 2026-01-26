from django.test import TestCase
from accounts.models import CustomUser, Profile


class CustomUserManagerTests(TestCase):
    def test_create_user_valid(self):
        user = CustomUser.objects.create_user(
            email="user@example.com",
            password="pass123",
            username="user1"
        )
        self.assertEqual(user.email, "user@example.com")
        self.assertTrue(user.check_password("pass123"))
        self.assertEqual(user.role, "student")
        self.assertEqual(user.username, "user1")

    def test_create_user_missing_email_raises(self):
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(email=None, password="pass123")

    def test_create_superuser_sets_admin_flags(self):
        admin = CustomUser.objects.create_superuser(
            email="admin@example.com",
            password="pass123",
            username="admin1"
        )
        self.assertEqual(admin.role, "admin")
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertEqual(admin.username, "admin1")


class CustomUserModelTests(TestCase):
    def setUp(self):
        self.student = CustomUser.objects.create_user(
            email="student@example.com",
            password="pass123",
            role="student"
        )
        self.instructor = CustomUser.objects.create_user(
            email="instructor@example.com",
            password="pass123",
            role="instructor"
        )
        # explicitly pass username to avoid duplicate keyword issues
        self.admin = CustomUser.objects.create_superuser(
            email="admin@example.com",
            password="pass123",
            username="adminuser"
        )

    def test_str_method_for_all_roles(self):
        self.assertEqual(str(self.student), "student@example.com (student)")
        self.assertEqual(str(self.instructor), "instructor@example.com (instructor)")
        self.assertEqual(str(self.admin), "admin@example.com (admin)")

    def test_role_helpers_positive_and_negative(self):
        # student
        self.assertTrue(self.student.is_student())
        self.assertFalse(self.student.is_instructor())
        self.assertFalse(self.student.is_admin())

        # instructor
        self.assertTrue(self.instructor.is_instructor())
        self.assertFalse(self.instructor.is_student())
        self.assertFalse(self.instructor.is_admin())

        # admin (superuser)
        self.assertTrue(self.admin.is_admin())
        self.assertFalse(self.admin.is_student())
        self.assertFalse(self.admin.is_instructor())

        # staff user should count as admin
        staff_user = CustomUser.objects.create_user(
            email="staff@example.com",
            password="pass123",
            role="student",
            is_staff=True
        )
        self.assertTrue(staff_user.is_admin())

        # superuser flag should count as admin
        superuser = CustomUser.objects.create_user(
            email="super@example.com",
            password="pass123",
            role="student",
            is_superuser=True
        )
        self.assertTrue(superuser.is_admin())

        # explicit role == "admin" branch
        role_admin = CustomUser.objects.create_user(
            email="roleadmin@example.com",
            password="pass123",
            role="admin"
        )
        self.assertTrue(role_admin.is_admin())


class ProfileModelTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="profile@example.com",
            password="pass123"
        )
        self.profile = self.user.profile  # created by signal

    def test_profile_str_method(self):
        self.assertEqual(str(self.profile), "Profile of profile@example.com")

    def test_signal_creates_profile_on_user_creation(self):
        self.assertIsInstance(self.user.profile, Profile)

    def test_signal_updates_profile_on_user_save(self):
        self.user.profile.bio = "Updated bio"
        self.user.save()  # triggers signal
        self.user.refresh_from_db()
        self.assertEqual(self.user.profile.bio, "Updated bio")

    def test_signal_handles_user_without_profile(self):
        # simulate a user without profile attribute
        user2 = CustomUser.objects.create_user(
            email="noprof@example.com",
            password="pass123"
        )
        # manually delete profile to simulate missing
        Profile.objects.filter(user=user2).delete()
        # saving should not error even if profile is missing
        user2.save()
        # profile should be recreated
        self.assertTrue(hasattr(user2, "profile"))

    def test_signal_updates_existing_profile(self):
        # ensure the save branch is hit
        self.user.profile.bio = "Another bio"
        self.user.profile.save()
        old_bio = self.user.profile.bio
        self.user.save()  # triggers signal update branch
        self.user.refresh_from_db()
        self.assertEqual(self.user.profile.bio, old_bio)
