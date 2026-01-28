from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from accounts.models import CustomUser, Profile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile information.
    Provides basic profile fields for nested inclusion.
    """
    class Meta:
        model = Profile
        fields = ["bio", "avatar", "location", "birth_date"]
        ref_name = "AccountsProfile"   # ✅ unique schema name to avoid conflicts


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer for listing and retrieving users.
    Includes nested profile information.
    """
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
            "role",
            "profile",
            "is_active",
            "is_staff",
        ]
        read_only_fields = ["id", "is_active", "is_staff"]

    def to_representation(self, instance):
        """
        Ensure null safety for nested profile.
        """
        representation = super().to_representation(instance)
        # ✅ safer null check: use getattr instead of hasattr
        if not getattr(instance, "profile", None):
            representation["profile"] = None
        return representation


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Handles password securely and creates user with role.
    """
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = CustomUser
        fields = ["username", "email", "password", "role"]

    def validate_email(self, value):
        """
        Ensure email is unique.
        """
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_password(self, value):
        """
        Validate password strength using Django's built-in validators.
        """
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def create(self, validated_data):
        """
        Create user with hashed password and default role.
        Automatically creates a profile for the user.
        """
        user = CustomUser.objects.create_user(
            username=validated_data.get("username"),
            email=validated_data["email"],
            password=validated_data["password"],
            role=validated_data.get("role", "student"),
        )
        # ✅ ensure profile is created safely
        Profile.objects.get_or_create(user=user)
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT serializer that uses email instead of username.
    Adds extra user info in the token response.
    """
    username_field = "email"

    def validate(self, attrs):
        data = super().validate(attrs)
        # ✅ safer null handling for role and username
        data.update({
            "id": self.user.id,
            "email": self.user.email,
            "username": getattr(self.user, "username", None),
            "role": getattr(self.user, "role", None),
        })
        return data
