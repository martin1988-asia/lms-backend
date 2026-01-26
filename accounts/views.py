from rest_framework import permissions, viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model

from .models import CustomUser, Profile
from .serializers import CustomUserSerializer, RegisterSerializer, ProfileSerializer


class RegisterView(APIView):
    """
    Public endpoint for user registration.
    Uses RegisterSerializer to validate and create a new user.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(RegisterSerializer(user).data, status=status.HTTP_201_CREATED)


class SignupView(APIView):
    """
    Alternate signup endpoint with a custom response payload.
    Returns a simplified JSON response after successful registration.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "message": "User created successfully",
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomUserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing CustomUser objects.
    Role-based isolation:
    - Admins: can list/retrieve all users.
    - Normal users: can only see their own account.
    """
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return CustomUser.objects.none()

        if getattr(user, "role", None) == "admin":
            return CustomUser.objects.all()
        return CustomUser.objects.filter(id=user.id)

    def create(self, request, *args, **kwargs):
        """
        Only admins can create users via this endpoint.
        Normal users should use /signup for registration.
        """
        user = request.user
        if getattr(user, "role", None) != "admin":
            return Response(
                {"detail": "Access denied. Only admins can create users here. Use /signup for registration."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """
        Custom endpoint to return the currently logged-in user.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class ProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user profiles.
    Role-based isolation:
    - Users: can only manage their own profile.
    - Admins: can manage all profiles.
    """
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, "role", None) == "admin":
            return Profile.objects.all()
        return Profile.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        profile = self.get_object()
        if profile.user != request.user and getattr(request.user, "role", None) != "admin":
            return Response(
                {"detail": "You do not have permission to update this profile."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        profile = self.get_object()
        if profile.user != request.user and getattr(request.user, "role", None) != "admin":
            return Response(
                {"detail": "You do not have permission to delete this profile."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT serializer that uses email instead of username.
    Adds extra user info in the token response.
    """
    username_field = "email"

    def validate(self, attrs):
        data = super().validate(attrs)
        data.update({
            "id": self.user.id,
            "email": self.user.email,
            "role": getattr(self.user, "role", None),
            "username": self.user.username,
        })
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT view wired to the serializer above.
    """
    serializer_class = CustomTokenObtainPairSerializer


# ✅ Forgot Password Views
UserModel = get_user_model()

class ForgotPasswordView(APIView):
    """
    Endpoint to request a password reset email.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        if not email:
            return Response({"detail": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        form = PasswordResetForm({"email": email})
        if form.is_valid():
            form.save(
                request=request,
                use_https=request.is_secure(),
                email_template_name="registration/password_reset_email.html",
            )
            return Response({"detail": "Password reset email sent"}, status=status.HTTP_200_OK)
        return Response({"detail": "Invalid email"}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordConfirmView(APIView):
    """
    Endpoint to confirm reset and set a new password.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = UserModel.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            form = SetPasswordForm(user, request.data)
            if form.is_valid():
                form.save()
                return Response({"detail": "Password has been reset"}, status=status.HTTP_200_OK)
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Invalid reset link"}, status=status.HTTP_400_BAD_REQUEST)
