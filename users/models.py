from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import CustomUser


class StudentProfile(models.Model):
    """
    Extended profile for students.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="student_profile")
    major = models.CharField(max_length=100, blank=True, null=True)
    year_of_study = models.IntegerField(blank=True, null=True)
    enrollment_date = models.DateField(blank=True, null=True)
    grade_level = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"StudentProfile for {self.user.email}"  # ✅ safer: always available


class InstructorProfile(models.Model):
    """
    Extended profile for instructors.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="instructor_profile")
    department = models.CharField(max_length=100, blank=True, null=True)
    hire_date = models.DateField(blank=True, null=True)
    expertise = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"InstructorProfile for {self.user.email}"  # ✅ safer: always available


class AdminProfile(models.Model):
    """
    Extended profile for admins.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="admin_profile")
    office = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"AdminProfile for {self.user.email}"  # ✅ safer: always available


# --- Signals ---
@receiver(post_save, sender=CustomUser)
def create_role_profiles(sender, instance, created, **kwargs):
    """
    Automatically create role-specific profiles when a CustomUser is created.
    """
    if created:
        if instance.role == "student":
            StudentProfile.objects.get_or_create(user=instance)
        elif instance.role == "instructor":
            InstructorProfile.objects.get_or_create(user=instance)
        elif instance.role == "admin":
            AdminProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=CustomUser)
def save_role_profiles(sender, instance, **kwargs):
    """
    Keep role-specific profiles updated if the user role changes.
    """
    if instance.role == "student" and getattr(instance, "student_profile", None):
        instance.student_profile.save()
    elif instance.role == "instructor" and getattr(instance, "instructor_profile", None):
        instance.instructor_profile.save()
    elif instance.role == "admin" and getattr(instance, "admin_profile", None):
        instance.admin_profile.save()
