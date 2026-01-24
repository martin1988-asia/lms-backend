from rest_framework import serializers
from accounts.models import CustomUser, Profile   # ✅ import from accounts


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile information (Accounts).
    """
    class Meta:
        model = Profile
        fields = ["bio", "avatar"]
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
            "date_joined",
        ]
        read_only_fields = ["id", "is_active", "is_staff", "date_joined"]


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

    def create(self, validated_data):
        """
        Create user with hashed password and default role.
        """
        user = CustomUser.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],  # ✅ automatically hashed
            role=validated_data.get("role", "student"),
        )
        # Ensure a profile is created automatically
        Profile.objects.get_or_create(user=user)
        return user
