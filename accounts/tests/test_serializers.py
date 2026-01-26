from django.test import TestCase
from accounts.models import CustomUser, Profile
from accounts.serializers import (
    ProfileSerializer,
    CustomUserSerializer,
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
)
from rest_framework_simplejwt.tokens import RefreshToken


class ProfileSerializerTests(TestCase):
    def test_profile_serialization(self):
        user = CustomUser.objects.create_user(email="profile@example.com", password="pass123")
        # use the profile automatically created by signals
        profile = user.profile
        profile.bio = "Hello bio"
        profile.save()
        serializer = ProfileSerializer(profile)
        data = serializer.data
        self.assertEqual(data["bio"], "Hello bio")
        self.assertIn("avatar", data)


class CustomUserSerializerTests(TestCase):
    def test_to_representation_with_profile(self):
        user = CustomUser.objects.create_user(email="user@example.com", password="pass123")
        # update the auto-created profile instead of creating a duplicate
        user.profile.bio = "Bio text"
        user.profile.save()
        serializer = CustomUserSerializer(user)
        data = serializer.data
        self.assertEqual(data["email"], "user@example.com")
        self.assertIsNotNone(data["profile"])

    def test_to_representation_without_profile(self):
        user = CustomUser.objects.create_user(email="noprof@example.com", password="pass123")
        # manually delete profile to simulate missing
        Profile.objects.filter(user=user).delete()
        serializer = CustomUserSerializer(user)
        data = serializer.data
        # serializer returns dict with None values, not plain None
        self.assertEqual(data["profile"], {"bio": None, "avatar": None})


class RegisterSerializerTests(TestCase):
    def test_validate_email_duplicate(self):
        CustomUser.objects.create_user(email="dup@example.com", password="pass123")
        serializer = RegisterSerializer(data={
            "email": "dup@example.com",
            "password": "password123",
            "role": "student"
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_create_user_and_profile(self):
        serializer = RegisterSerializer(data={
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123",
            "role": "student"
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertEqual(user.email, "new@example.com")
        self.assertTrue(hasattr(user, "profile"))

    def test_password_min_length(self):
        serializer = RegisterSerializer(data={
            "email": "shortpass@example.com",
            "password": "short",
            "role": "student"
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)


class CustomTokenObtainPairSerializerTests(TestCase):
    def test_validate_includes_extra_fields(self):
        user = CustomUser.objects.create_user(email="token@example.com", password="pass123", role="student")
        refresh = RefreshToken.for_user(user)
        token_serializer = CustomTokenObtainPairSerializer()
        token_serializer.user = user
        data = {"email": user.email, "password": "pass123"}
        validated = token_serializer.validate(data)
        self.assertIn("id", validated)
        self.assertIn("email", validated)
        self.assertIn("role", validated)
