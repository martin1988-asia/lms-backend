from django.conf import settings
from django.db import models
from assignments.models import Submission


class Grade(models.Model):
    """
    Represents a grade given by an instructor for a submission.
    """
    submission = models.OneToOneField(
        Submission,
        on_delete=models.CASCADE,
        related_name="grade_record",   # ✅ changed from "grade" to avoid clash
        help_text="Submission being graded"
    )
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="grades_given",
        help_text="Instructor who graded the submission"
    )
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Numeric score (e.g., 85.50)"
    )
    letter = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        help_text="Letter grade (e.g., A, B, C)"
    )
    feedback = models.TextField(
        blank=True,
        null=True,
        help_text="Instructor feedback"
    )
    graded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-graded_at"]
        verbose_name = "Grade"
        verbose_name_plural = "Grades"

    def __str__(self):
        # ✅ Guard against missing student or username to avoid Swagger/AnonymousUser errors
        student_name = getattr(self.submission.student, "username", "Unknown")
        return f"{student_name} → {self.letter or self.score}"

    def save(self, *args, **kwargs):
        """
        Override save to also update the Submission.grade field
        for quick analytics access.
        """
        super().save(*args, **kwargs)
        if self.score is not None:
            # ✅ Guard to ensure Submission has a grade field before assignment
            if hasattr(self.submission, "grade"):
                self.submission.grade = self.score
                self.submission.save(update_fields=["grade"])
