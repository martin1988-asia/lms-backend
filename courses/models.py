from django.conf import settings
from django.db import models


class Course(models.Model):
    """
    Represents a course taught by an instructor.
    """
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courses",
        help_text="Instructor responsible for this course"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]
        verbose_name = "Course"
        verbose_name_plural = "Courses"

    def __str__(self):
        # ✅ safer: always use email if username is missing
        instructor_name = getattr(self.instructor, "username", None) or self.instructor.email
        return f"{self.title} (Instructor: {instructor_name})"


class Enrollment(models.Model):
    """
    Represents a student's enrollment in a course.
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollments",
        help_text="Student enrolled in the course"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments",
        help_text="Course the student is enrolled in"
    )
    date_enrolled = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "course")
        ordering = ["-date_enrolled"]
        verbose_name = "Enrollment"
        verbose_name_plural = "Enrollments"

    def __str__(self):
        # ✅ safer: fallback to email if username is missing
        student_name = getattr(self.student, "username", None) or self.student.email
        return f"{student_name} enrolled in {self.course.title}"


class Module(models.Model):
    """
    Represents a module within a course.
    """
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="modules",
        help_text="Course this module belongs to"
    )
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]
        verbose_name = "Module"
        verbose_name_plural = "Modules"

    def __str__(self):
        return f"{self.title} ({self.course.title})"
