from django.conf import settings
from django.db import models
from courses.models import Course, Module


class Assignment(models.Model):
    """
    Represents an assignment within a course/module.
    """
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="assignments",
        help_text="Course this assignment belongs to"
    )
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name="assignments",
        null=True,
        blank=True,
        help_text="Optional module this assignment belongs to"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateTimeField(help_text="Deadline for submission")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_assignments",
        null=True,
        blank=True,
        help_text="Instructor who created the assignment"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["course", "title"], name="unique_assignment_per_course")
        ]
        ordering = ["due_date"]
        verbose_name = "Assignment"
        verbose_name_plural = "Assignments"

    def __str__(self):
        # ✅ Guard against missing course to avoid crashes in Swagger or admin
        course_title = getattr(self.course, "title", "Unknown Course")
        return f"{self.title} ({course_title})"


class Submission(models.Model):
    """
    Represents a student's submission for an assignment.
    """
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name="submissions",
        help_text="Assignment this submission belongs to"
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="submissions",
        help_text="Student who submitted"
    )
    content = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    feedback = models.TextField(blank=True, null=True)
    grade = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Optional numeric grade for this submission"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["assignment", "student"], name="unique_submission_per_student")
        ]
        ordering = ["-submitted_at"]
        verbose_name = "Submission"
        verbose_name_plural = "Submissions"

    def __str__(self):
        # ✅ Guard against missing student or assignment to avoid crashes in Swagger or admin
        student_name = getattr(self.student, "username", "Unknown Student")
        assignment_title = getattr(self.assignment, "title", "Unknown Assignment")
        return f"{student_name} → {assignment_title}"
