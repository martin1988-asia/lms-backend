from django.test import TestCase
from rest_framework.test import APIRequestFactory
from accounts.permissions import RolePermission, IsStudent, IsInstructor, IsAdmin, ReadOnly
from accounts.models import CustomUser


class RolePermissionTests(TestCase):
    """
    Comprehensive test suite for RolePermission and its subclasses.
    Covers all branches: read-only, unauthenticated, staff/superuser override,
    role matches, role mismatch, and __str__ output.
    """

    def setUp(self):
        self.factory = APIRequestFactory()

        # Users with different roles
        self.student = CustomUser.objects.create_user(
            email="student@example.com",
            password="password123",
            role="student"
        )
        self.instructor = CustomUser.objects.create_user(
            email="instructor@example.com",
            password="password123",
            role="instructor"
        )
        self.admin = CustomUser.objects.create_user(
            email="admin@example.com",
            password="password123",
            role="admin"
        )
        self.staff = CustomUser.objects.create_user(
            email="staff@example.com",
            password="password123",
            role="student",
            is_staff=True
        )
        # explicitly pass username to avoid duplicate keyword issues
        self.superuser = CustomUser.objects.create_superuser(
            email="super@example.com",
            password="password123",
            username="superuser1"
        )

    def test_read_only_allows_safe_methods(self):
        request = self.factory.get("/")
        request.user = self.student
        perm = ReadOnly()
        self.assertTrue(perm.has_permission(request, None))

    def test_read_only_denies_non_safe_methods(self):
        request = self.factory.post("/")
        request.user = self.student
        perm = ReadOnly()
        self.assertFalse(perm.has_permission(request, None))

    def test_unauthenticated_user_denied(self):
        request = self.factory.get("/")
        request.user = type("Anonymous", (), {"is_authenticated": False})()
        perm = RolePermission()
        self.assertFalse(perm.has_permission(request, None))

    def test_staff_override_allowed(self):
        request = self.factory.get("/")
        request.user = self.staff
        perm = RolePermission()
        self.assertTrue(perm.has_permission(request, None))

    def test_superuser_override_allowed(self):
        request = self.factory.get("/")
        request.user = self.superuser
        perm = RolePermission()
        self.assertTrue(perm.has_permission(request, None))

    def test_role_match_allowed(self):
        request = self.factory.get("/")
        request.user = self.student
        perm = IsStudent()
        self.assertTrue(perm.has_permission(request, None))

    def test_role_mismatch_denied(self):
        request = self.factory.get("/")
        request.user = self.instructor
        perm = IsStudent()
        self.assertFalse(perm.has_permission(request, None))

    def test_is_instructor_permission(self):
        request = self.factory.get("/")
        request.user = self.instructor
        perm = IsInstructor()
        self.assertTrue(perm.has_permission(request, None))

    def test_is_admin_permission(self):
        request = self.factory.get("/")
        request.user = self.admin
        perm = IsAdmin()
        self.assertTrue(perm.has_permission(request, None))

    def test_str_representation(self):
        perm = IsAdmin()
        self.assertEqual(str(perm), "RolePermission(roles=['admin'], read_only=False)")
