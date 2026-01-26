from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.serializers import (
    RegisterSerializer,
    CustomUserSerializer,
    ProfileSerializer,
    CustomTokenObtainPairSerializer,
)
from accounts.models import Profile

User = get_user_model()


class RegisterSerializerTests(TestCase):
    """
    Tests for RegisterSerializer.
    Validates email uniqueness, password strength, and profile auto-creation.
    """

    def test_register_serializer_creates_user_and_profile(self):
        data = {
            "username": "serializeruser",
            "email": "serializer@example.com",
            "password": "StrongPass123!",
            "role": "student",
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertTrue(User.objects.filter(email="serializer@example.com").exists())
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_register_serializer_rejects_duplicate_email(self):
        User.objects.create_user(email="dup@example.com", password="securePass123")
        data = {
            "username": "dupuser",
            "email": "dup@example.com",
            "password": "securePass123",
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_register_serializer_rejects_weak_password(self):
        data = {
            "username": "weakuser",
            "email": "weak@example.com",
            "password": "123",
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)


class CustomUserSerializerTests(TestCase):
    """
    Tests for CustomUserSerializer.
    Ensures profile is included and null-safe.
    """

    def test_custom_user_serializer_includes_profile(self):
        user = User.objects.create_user(email="profile@example.com", password="securePass123")
        Profile.objects.get_or_create(user=user, bio="Hello world")
        serializer = CustomUserSerializer(user)
        self.assertIn("profile", serializer.data)
        self.assertEqual(serializer.data["profile"]["bio"], "Hello world")

    def test_custom_user_serializer_handles_missing_profile(self):
        user = User.objects.create_user(email="noprofile@example.com", password="securePass123")
        serializer = CustomUserSerializer(user)
        self.assertIn("profile", serializer.data)
        self.assertIsNone(serializer.data["profile"])


class ProfileSerializerTests(TestCase):
    """
    Tests for ProfileSerializer.
    Ensures updates are applied correctly.
    """

    def test_profile_serializer_updates_fields(self):
        user = User.objects.create_user(email="update@example.com", password="securePass123")
        profile = Profile.objects.get(user=user)
        data = {"bio": "Updated bio", "location": "Windhoek"}
        serializer = ProfileSerializer(profile, data=data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated_profile = serializer.save()
        self.assertEqual(updated_profile.bio, "Updated bio")
        self.assertEqual(updated_profile.location, "Windhoek")


class CustomTokenObtainPairSerializerTests(TestCase):
    """
    Tests for CustomTokenObtainPairSerializer.
    Ensures JWT payload includes extra user info.
    """

    def test_token_serializer_includes_user_info(self):
        user = User.objects.create_user(
            email="token@example.com", password="securePass123", username="tokenuser", role="student"
        )
        serializer = CustomTokenObtainPairSerializer()
        serializer.user = user
        data = {"access": "dummy_access", "refresh": "dummy_refresh"}
        validated = serializer.validate({"email": user.email, "password": "securePass123"})
        self.assertIn("id", validated)
        self.assertEqual(validated["email"], "token@example.com")
        self.assertEqual(validated["role"], "student")
        self.assertEqual(validated["username"], "tokenuser")
