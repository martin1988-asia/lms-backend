from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import CustomUser


class StudentProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="student_profile")
    major = models.CharField(max_length=100, blank=True, null=True)
    year_of_study = models.IntegerField(blank=True, null=True)
    enrollment_date = models.DateField(blank=True, null=True)   # added
    grade_level = models.CharField(max_length=50, blank=True, null=True)  # added

    def __str__(self):
        return f"StudentProfile for {self.user.username}"


class InstructorProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="instructor_profile")
    department = models.CharField(max_length=100, blank=True, null=True)
    hire_date = models.DateField(blank=True, null=True)   # added
    expertise = models.CharField(max_length=100, blank=True, null=True)  # added

    def __str__(self):
        return f"InstructorProfile for {self.user.username}"


class AdminProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="admin_profile")
    office = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"AdminProfile for {self.user.username}"


# Automatically create role-specific profiles when a CustomUser is created
@receiver(post_save, sender=CustomUser)
def create_role_profiles(sender, instance, created, **kwargs):
    if created:
        if instance.role == "student":
            StudentProfile.objects.create(user=instance)
        elif instance.role == "instructor":
            InstructorProfile.objects.create(user=instance)
        elif instance.role == "admin":
            AdminProfile.objects.create(user=instance)


# Optional: keep profiles updated if role changes
@receiver(post_save, sender=CustomUser)
def save_role_profiles(sender, instance, **kwargs):
    if instance.role == "student" and hasattr(instance, "student_profile"):
        instance.student_profile.save()
    elif instance.role == "instructor" and hasattr(instance, "instructor_profile"):
        instance.instructor_profile.save()
    elif instance.role == "admin" and hasattr(instance, "admin_profile"):
        instance.admin_profile.save()
