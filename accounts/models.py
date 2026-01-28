from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    """
    Custom manager that uses email as the unique identifier instead of username.
    """

    def create_user(self, email, password=None, role="student", username=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, username=None, **extra_fields):
        """
        Create and return a superuser with admin role and proper flags.
        """
        extra_fields.setdefault("role", "admin")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email=email, password=password, username=username, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model with role support for LMS.
    Uses email as the unique identifier for authentication.
    """

    ROLE_CHOICES = (
        ("student", "Student"),
        ("instructor", "Instructor"),
        ("admin", "Admin"),
    )

    username = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="student",
        help_text="Defines the role of the user in the LMS"
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"   # ✅ login by email
    REQUIRED_FIELDS = []       # ✅ no username required

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email} ({self.role})"

    # --- Role helpers ---
    def is_student(self):
        return self.role == "student"

    def is_instructor(self):
        return self.role == "instructor"

    def is_admin(self):
        return self.role == "admin" or self.is_staff or self.is_superuser


class Profile(models.Model):
    """
    Profile model for storing extra user information.
    Linked one-to-one with CustomUser.
    """
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    preferences = models.JSONField(default=dict, blank=True)  # ✅ flexible for future personalization

    def __str__(self):
        return f"Profile of {self.user.email}"


# --- Signals ---
@receiver(post_save, sender=CustomUser)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create or update Profile when a CustomUser is created/updated.
    """
    if created:
        Profile.objects.get_or_create(user=instance)
    else:
        # ✅ safer null check before saving profile
        if getattr(instance, "profile", None):
            instance.profile.save()
