from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class CustomUser(AbstractUser):
    """
    Custom user model with role support for LMS.
    Extends Django's AbstractUser to include unique email and role field.
    """

    ROLE_CHOICES = (
        ("student", "Student"),
        ("instructor", "Instructor"),
        ("admin", "Admin"),
    )

    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="student",
        help_text="Defines the role of the user in the LMS"
    )

    def __str__(self):
        return f"{self.username} ({self.role})"

    # --- Role helpers ---
    def is_student(self):
        return self.role == "student"

    def is_instructor(self):
        return self.role == "instructor"

    def is_admin(self):
        # Allow both custom 'admin' role and Django's built-in staff/superuser
        return self.role == "admin" or self.is_staff or self.is_superuser


class Profile(models.Model):
    """
    Optional profile model for storing extra user information.
    Linked one-to-one with CustomUser.
    """

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    def __str__(self):
        return f"Profile of {self.user.username}"


# --- Signals ---
@receiver(post_save, sender=CustomUser)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create or update Profile when a CustomUser is created/updated.
    """
    if created:
        Profile.objects.create(user=instance)
    else:
        # Defensive check: only save if profile exists
        if hasattr(instance, "profile"):
            instance.profile.save()
